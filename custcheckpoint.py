# library
import numpy as np
import tensorflow as tf
import six
import re
import os

from tensorflow import keras
from tensorflow.python.keras.utils.io_utils import path_to_string
from tensorflow.python.training.saving import checkpoint_options as checkpoint_options_lib
from tensorflow.python.saved_model import save_options as save_options_lib
from tensorflow.python.keras.utils import tf_utils
from tensorflow.python.platform import tf_logging as logging
from tensorflow.python.distribute import distributed_file_utils
from tensorflow.python.lib.io import file_io
from tensorflow.python.training import checkpoint_management

class ModelCheckpoint(keras.callbacks.Callback):
  '''   
  Example:
  EPOCHS = 10
  checkpoint_filepath = '/tmp/checkpoint'
  model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
      filepath=checkpoint_filepath,
      save_weights_only=True,
      monitor='val_acc',
      mode='max',
      save_best_only=True)
  # Model weights are saved at the end of every epoch, if it's the best seen
  # so far.
  model.fit(epochs=EPOCHS, callbacks=[model_checkpoint_callback])
  # The model weights (that are considered the best) are loaded into the model.
  model.load_weights(checkpoint_filepath)
  '''

  def __init__(self,
               filepath,
               monitor='val_loss',
               verbose=0,
               save_best_only=False,
               save_weights_only=False,
               mode='auto',
               save_freq='epoch',
               options=None,
               **kwargs):
    super(ModelCheckpoint, self).__init__()
    self._supports_tf_logs = True
    self.monitor = monitor
    self.verbose = verbose
    self.filepath = path_to_string(filepath)
    self.save_best_only = save_best_only
    self.save_weights_only = save_weights_only
    self.save_freq = save_freq
    self.epochs_since_last_save = 0
    self._batches_seen_since_last_saving = 0
    self._last_batch_seen = 0

    if save_weights_only:
      if options is None or isinstance(
          options, checkpoint_options_lib.CheckpointOptions):
        self._options = options or checkpoint_options_lib.CheckpointOptions()
      else:
        raise TypeError('If save_weights_only is True, then `options` must be'
                        'either None or a tf.train.CheckpointOptions')
    else:
      if options is None or isinstance(options, save_options_lib.SaveOptions):
        self._options = options or save_options_lib.SaveOptions()
      else:
        raise TypeError('If save_weights_only is False, then `options` must be'
                        'either None or a tf.saved_model.SaveOptions')

    # Deprecated field `load_weights_on_restart` is for loading the checkpoint
    # file from `filepath` at the start of `model.fit()`
    # TODO(rchao): Remove the arg during next breaking release.
    if 'load_weights_on_restart' in kwargs:
      self.load_weights_on_restart = kwargs['load_weights_on_restart']
      logging.warning('`load_weights_on_restart` argument is deprecated. '
                      'Please use `model.load_weights()` for loading weights '
                      'before the start of `model.fit()`.')
    else:
      self.load_weights_on_restart = False

    # Deprecated field `period` is for the number of epochs between which
    # the model is saved.
    if 'period' in kwargs:
      self.period = kwargs['period']
      logging.warning('`period` argument is deprecated. Please use `save_freq` '
                      'to specify the frequency in number of batches seen.')
    else:
      self.period = 1

    if mode not in ['auto', 'min', 'max']:
      logging.warning('ModelCheckpoint mode %s is unknown, '
                      'fallback to auto mode.', mode)
      mode = 'auto'

    if mode == 'min':
      self.monitor_op = np.less
      self.best = np.Inf
    elif mode == 'max':
      self.monitor_op = np.greater
      self.best = -np.Inf
    else:
      if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
        self.monitor_op = np.greater
        self.best = -np.Inf
      else:
        self.monitor_op = np.less
        self.best = np.Inf

    if self.save_freq != 'epoch' and not isinstance(self.save_freq, int):
      raise ValueError('Unrecognized save_freq: {}'.format(self.save_freq))

    # Only the chief worker writes model checkpoints, but all workers
    # restore checkpoint at on_train_begin().
    self._chief_worker_only = False

  def set_model(self, model):
    self.model = model
    # Use name matching rather than `isinstance` to avoid circular dependencies.
    if (not self.save_weights_only and
        not model._is_graph_network and  # pylint: disable=protected-access
        model.__class__.__name__ != 'Sequential'):
      self.save_weights_only = True

  def on_train_begin(self, logs=None):
    if self.load_weights_on_restart:
      filepath_to_load = (
          self._get_most_recently_modified_file_matching_pattern(self.filepath))
      if (filepath_to_load is not None and
          self._checkpoint_exists(filepath_to_load)):
        try:
          # `filepath` may contain placeholders such as `{epoch:02d}`, and
          # thus it attempts to load the most recently modified file with file
          # name matching the pattern.
          self.model.load_weights(filepath_to_load)
        except (IOError, ValueError) as e:
          raise ValueError('Error loading file from {}. Reason: {}'.format(
              filepath_to_load, e))

  def on_train_batch_end(self, batch, logs=None):
    if self._should_save_on_batch(batch):
      self._save_model(epoch=self._current_epoch, logs=logs)

  def on_epoch_begin(self, epoch, logs=None):
    self._current_epoch = epoch

  def on_epoch_end(self, epoch, logs=None):
    self.epochs_since_last_save += 1
    # pylint: disable=protected-access
    # MOD
    print("Start record {}".format(epoch))
    with open ("tmp/check_epoch.txt", "w") as wf:
        wf.write(str(epoch + 1))        
    #MOD
    if self.save_freq == 'epoch':
      self._save_model(epoch=epoch, logs=logs)

  def _should_save_on_batch(self, batch):
    """Handles batch-level saving logic, supports steps_per_execution."""
    if self.save_freq == 'epoch':
      return False

    if batch <= self._last_batch_seen:  # New epoch.
      add_batches = batch + 1  # batches are zero-indexed.
    else:
      add_batches = batch - self._last_batch_seen
    self._batches_seen_since_last_saving += add_batches
    self._last_batch_seen = batch

    if self._batches_seen_since_last_saving >= self.save_freq:
      self._batches_seen_since_last_saving = 0
      return True
    return False

  def _save_model(self, epoch, logs):
    """Saves the model.
    Arguments:
        epoch: the epoch this iteration is in.
        logs: the `logs` dict passed in to `on_batch_end` or `on_epoch_end`.
    """
    logs = logs or {}

    if isinstance(self.save_freq,
                  int) or self.epochs_since_last_save >= self.period:
      # Block only when saving interval is reached.
      logs = tf_utils.to_numpy_or_python_type(logs)
      self.epochs_since_last_save = 0
      filepath = self._get_file_path(epoch, logs)

      try:
        if self.save_best_only:
          current = logs.get(self.monitor)
          if current is None:
            logging.warning('Can save best model only with %s available, '
                            'skipping.', self.monitor)
          else:
            if self.monitor_op(current, self.best):
              if self.verbose > 0:
                print('\nEpoch %05d: %s improved from %0.5f to %0.5f,'
                      ' saving model to %s' % (epoch + 1, self.monitor,
                                               self.best, current, filepath))
              self.best = current
              if self.save_weights_only:
                self.model.save_weights(
                    filepath, overwrite=True, options=self._options)
              else:
                self.model.save(filepath, overwrite=True, options=self._options)
            else:
              if self.verbose > 0:
                print('\nEpoch %05d: %s did not improve from %0.5f' %
                      (epoch + 1, self.monitor, self.best))
        else:
          if self.verbose > 0:
            print('\nEpoch %05d: saving model to %s' % (epoch + 1, filepath))
          if self.save_weights_only:
            self.model.save_weights(
                filepath, overwrite=True, options=self._options)
          else:
            self.model.save(filepath, overwrite=True, options=self._options)

        self._maybe_remove_file()
      except IOError as e:
        # `e.errno` appears to be `None` so checking the content of `e.args[0]`.
        if 'is a directory' in six.ensure_str(e.args[0]).lower():
          raise IOError('Please specify a non-directory filepath for '
                        'ModelCheckpoint. Filepath used is an existing '
                        'directory: {}'.format(filepath))

  def _get_file_path(self, epoch, logs):
    """Returns the file path for checkpoint."""
    # pylint: disable=protected-access
    try:
      # `filepath` may contain placeholders such as `{epoch:02d}` and
      # `{mape:.2f}`. A mismatch between logged metrics and the path's
      # placeholders can cause formatting to fail.
      file_path = self.filepath.format(epoch=epoch + 1, **logs)
    except KeyError as e:
      raise KeyError('Failed to format this callback filepath: "{}". '
                     'Reason: {}'.format(self.filepath, e))
    self._write_filepath = distributed_file_utils.write_filepath(
        file_path, self.model.distribute_strategy)
    return self._write_filepath

  def _maybe_remove_file(self):
    # Remove the checkpoint directory in multi-worker training where this worker
    # should not checkpoint. It is a dummy directory previously saved for sync
    # distributed training.
    distributed_file_utils.remove_temp_dir_with_filepath(
        self._write_filepath, self.model.distribute_strategy)

  def _checkpoint_exists(self, filepath):
    """Returns whether the checkpoint `filepath` refers to exists."""
    if filepath.endswith('.h5'):
      return file_io.file_exists(filepath)
    tf_saved_model_exists = file_io.file_exists(filepath)
    tf_weights_only_checkpoint_exists = file_io.file_exists(filepath + '.index')
    return tf_saved_model_exists or tf_weights_only_checkpoint_exists

  def _get_most_recently_modified_file_matching_pattern(self, pattern):
    
    dir_name = os.path.dirname(pattern)
    base_name = os.path.basename(pattern)
    base_name_regex = '^' + re.sub(r'{.*}', r'.*', base_name) + '$'

    # If tf.train.latest_checkpoint tells us there exists a latest checkpoint,
    # use that as it is more robust than `os.path.getmtime()`.
    latest_tf_checkpoint = checkpoint_management.latest_checkpoint(dir_name)
    if latest_tf_checkpoint is not None and re.match(
        base_name_regex, os.path.basename(latest_tf_checkpoint)):
      return latest_tf_checkpoint

    latest_mod_time = 0
    file_path_with_latest_mod_time = None
    n_file_with_latest_mod_time = 0
    file_path_with_largest_file_name = None

    if file_io.file_exists(dir_name):
      for file_name in os.listdir(dir_name):
        # Only consider if `file_name` matches the pattern.
        if re.match(base_name_regex, file_name):
          file_path = os.path.join(dir_name, file_name)
          mod_time = os.path.getmtime(file_path)
          if (file_path_with_largest_file_name is None or
              file_path > file_path_with_largest_file_name):
            file_path_with_largest_file_name = file_path
          if mod_time > latest_mod_time:
            latest_mod_time = mod_time
            file_path_with_latest_mod_time = file_path
            # In the case a file with later modified time is found, reset
            # the counter for the number of files with latest modified time.
            n_file_with_latest_mod_time = 1
          elif mod_time == latest_mod_time:
            # In the case a file has modified time tied with the most recent,
            # increment the counter for the number of files with latest modified
            # time by 1.
            n_file_with_latest_mod_time += 1

    if n_file_with_latest_mod_time == 1:
      # Return the sole file that has most recent modified time.
      return file_path_with_latest_mod_time
    else:
      # If there are more than one file having latest modified time, return
      # the file path with the largest file name.
      return file_path_with_largest_file_name
