class TgCommand(object):
    def __init__(self, name, help_text, awaitable_action_method, enabled=False, pattern=None):
        self.name = name
        self.pattern = pattern
        self.help_text = help_text
        self.awaitable_action_method = awaitable_action_method
        self.enabled = enabled

    def apply_and_get_awaitable(self, bot, message, **kwargs):
        kwargs['command_name'] = self.name
        return self.awaitable_action_method(bot, message, **kwargs)
