class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class WfsError(Exception):
    """Base class for exceptions in this package."""

    base_msg_general = f'{Color.RED}ERROR:{Color.END} {Color.BOLD}wiki-film-scraper{Color.END} raised an exception.'
    base_msg_specific = 'An error occurred.'

    def __init__(self, *args, **kwargs):
        if any(args):
            self.msg = args[0]
        elif kwargs:
            self.error_type = kwargs.get('error_type')
            if self.error_type:
                self.msg = self.base_msg_specific[:-1] + f' with: {Color.CYAN + self.error_type.upper() + Color.END}'
        else:
            self.msg = self.base_msg_specific
    
    def __str__(self):
        return f'\n{self.base_msg_general}\n{self.msg}'


class ChoicesError(WfsError):
    """Class for exceptions related to the choices input parameter."""

    def __init__(self, *args, **kwargs):
        if not any(args):
            kwargs['error_type'] = 'choices input'
        super().__init__(*args, **kwargs)


class PagesError(WfsError):
    """Class for exceptions related to the use of local HTML pages."""

    def __init__(self, *args, **kwargs):
        if not any(args):
            kwargs['error_type'] = 'local pages'
        super().__init__(*args, **kwargs)


def main(exc, msg=None):
    if exc == 'wfs':
        raise WfsError(msg)
    elif exc == 'choices':
        raise ChoicesError(msg)
    elif exc == 'pages':
        raise PagesError(msg)


if __name__ == '__main__':
    test_exc = 'wfs'
    test_msg = None
    main(test_exc, test_msg)