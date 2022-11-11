class ParseException(ValueError):
    msg = "Parse Error"


class ParseExceptionCanSkip(ValueError):
    msg = "Parse Error where possible skip"


class HeaderNotFoundException(ParseExceptionCanSkip):
    msg = "Bot header has been not found in service"


class CommandNotFoundException(ParseExceptionCanSkip):
    msg = "Command has been not found in service"


class CommandParameterNotFoundException(ParseExceptionCanSkip):
    msg = "Commands parameters has been not found in service"


class CommandKeyValueInvalidException(ParseException):
    msg = "Commands parameters with key=value mask not found"
