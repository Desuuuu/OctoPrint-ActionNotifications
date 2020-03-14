$(function() {
  function ActionNotificationsViewModel() {
    var self = this;

    self.messages = {};

    self.onDataUpdaterPluginMessage = function(plugin, data) {
      if (plugin !== 'actionnotifications' || typeof data !== 'object' || !data) {
        return;
      }

      if (!self.messages.hasOwnProperty(data.type) || !self.messages[data.type]) {
        self.messages[data.type] = [];
      }

      if (data.noduplicate && self.messages[data.type].indexOf(data.text) >= 0) {
        return;
      }

      self.messages[data.type].push(data.text);

      var options = {
        title: 'Printer notification',
        text: data.text,
        type: data.type,
        after_close: function(notification) {
          if (!self.messages.hasOwnProperty(notification.options.type)) {
            return;
          }

          var index = self.messages[notification.options.type].indexOf(notification.options.text);

          if (index >= 0) {
            self.messages[notification.options.type].splice(index, 1);
          }
        }
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

  function CustomSettingsViewModel(parameters) {
    var self = this;

    self.filters = ko.observableArray();

    self.onBeforeBinding = function() {
      self.settings = parameters[0].settings;

      self.filters(self.settings.plugins.actionnotifications.filters.slice(0).map(function(filter) {
        return {
          content: filter.trim()
        };
      }).filter(function(filter) {
        return filter.content.length > 0;
      }));
    };

    self.onSettingsBeforeSave = function () {
      self.filters(self.filters.slice(0).map(function(filter) {
        return {
          content: filter.content.trim()
        };
      }).filter(function(filter) {
        return filter.content.length > 0;
      }));

      self.settings.plugins.actionnotifications.filters(self.filters.slice(0).map(function(filter) {
        return filter.content;
      }));
    }

    self.addFilter = function() {
      self.filters.push({ content: '' });
    };

    self.removeFilter = function(index) {
      self.filters.splice(index(), 1);
    };
  }

  OCTOPRINT_VIEWMODELS.push({
    construct: ActionNotificationsViewModel
  }, {
    construct: CustomSettingsViewModel,
    dependencies: ['settingsViewModel'],
    elements: ['#settings_plugin_actionnotifications']
  });
});
