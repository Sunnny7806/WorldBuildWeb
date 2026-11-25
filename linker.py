import re #Metin içeriisnde kelime arama kütüphanesi
from worldManager import WorldManager

#AÇIKLAMA METİNLERİNDE DATABASE DE OLAAN BİR İSMİN GEÇİP GEÇMEDİĞİNİ İNCELEYEN KOD.

class WikiLinker:
    #bişiler...
    LINK_PATTERN = re.compile(r'\[([^\[\]|]+)(?:\|[^\[\]]+)?\]')
    @staticmethod
    def buildAliasMap():
        entities = WorldManager.get_all_entities()
        aliasMap = {}

        for e in entities:
            aliasMap[e.name.strip().lower()] = e
            if e.aliases:
                alias_list = [a.strip() for a in e.aliases.split(",") if a.strip()]
                for alias in alias_list:
                    aliasMap[alias.lower()] = e

        return aliasMap

    @staticmethod
    def autoLink(text:str) -> str:
        aliasMap = WikiLinker.buildAliasMap()
        if not aliasMap: return text

        sorted_keywords = sorted(aliasMap.keys(),key=len,reverse=True)
        #Link bağlarken iki kere çağrılırsa çift parantez oluşmasın diye
        patternStr = r'(\[[^\]]*\])|\b(' + '|'.join(re.escape(k) for k in sorted_keywords) + r')\b'
        regex = re.compile(patternStr, flags=re.IGNORECASE)

        #Her eşleşme bulunduğunda callback atması için var
        def replaceMatch(match):
            #Bir kelimeyi bir kere bağladıktan sonra artık o kelimeden tekrar tekrar linkk oluşturmaz.
            if match.group(1):
                return match.group(1)
            matchedWords = match.group(2)
            

            #Küçük büyük harf uyumu için
            entity = None
            entity = aliasMap.get(matchedWords.lower())

            if not entity:
                return matchedWords

            #Eğer metinde geçen asıl kelimeyse
            if matchedWords.lower() == entity.name.lower():
                return(f"[{entity.name}]")
            else:
                #Eğer bir takma ad ise
                return(f"[{entity.name}|{matchedWords}]")

        linkedText = regex.sub(replaceMatch,text)
        return linkedText

    @staticmethod
    def extractLinks(text: str) -> set:
        return {name.strip() for name in WikiLinker.LINK_PATTERN.findall(text)}
