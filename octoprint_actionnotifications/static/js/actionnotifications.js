$(function() {
  function ActionNotificationsViewModel() {
    var self = this;

    self.onDataUpdaterPluginMessage = function(plugin, data) {
      if (plugin !== 'actionnotifications' || typeof data !== 'object' || !data) {
        return;
      }

      var options = {
        title: 'Printer notification',
        text: data.text,
        type: data.type
      };

      if (data.duration <= 0) {
        options.hide = false;
      } else {
        options.hide = true;
        options.delay = data.duration * 1000;
      }

      new PNotify(options);
    };
  }

  OCTOPRINT_VIEWMODELS.push({
    construct: ActionNotificationsViewModel
  });
});
