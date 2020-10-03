class TgCommand(object):
    def __init__(self, names, help_text, awaitable_action_method, enabled=False, pattern=None):
        if isinstance(names, str):
            names = [names]
        self.names = names
        self.pattern = pattern
        self.help_text = help_text
        self.awaitable_action_method = awaitable_action_method
        self.enabled = enabled

    def apply_and_get_awaitable(self, message, manager, **kwargs):
        command_name = message.text.split(' ', maxsplit=1)[0].lstrip('/')
        # assert command_name in self.names, (command_name, self.names)
        kwargs['command_name'] = command_name
        return self.awaitable_action_method(message, manager, **kwargs)
