from dadata import DadataAsync

from xshared.config import settings


async def dd_find_by_id(subject: str, query: str):
    async with DadataAsync(settings.dd_token, settings.dd_secret) as dadata:
        return await dadata.find_by_id(name=subject, query=query)


async def dd_suggest(subject: str, query: str):
    async with DadataAsync(settings.dd_token, settings.dd_secret) as dadata:
        return await dadata.suggest(name=subject, query=query)
