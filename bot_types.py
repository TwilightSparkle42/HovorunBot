from telegram.ext import CallbackContext, ExtBot

type ADict = dict[str, str]

type Context = CallbackContext[ExtBot[None], ADict, ADict, ADict]
