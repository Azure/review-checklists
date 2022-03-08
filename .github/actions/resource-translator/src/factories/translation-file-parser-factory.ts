import { TranslationFileKind } from "../abstractions/translation-file-kind";
import { JsonParser } from "../parsers/json-parser";
import { PortableObjectParser } from "../parsers/po-parser";
import { RestextParser } from "../parsers/restext-parser";
import { ResxParser } from "../parsers/resx-parser";
import { TranslationFileParser } from "../parsers/translation-file-parser";
import { XliffParser } from "../parsers/xliff-parser";

export const translationFileParserFactory = (translationFileKind: TranslationFileKind): TranslationFileParser => {
    switch (translationFileKind) {
        case 'resx': return new ResxParser();
        case 'xliff': return new XliffParser();
        case 'restext': return new RestextParser();
        case 'ini': return new RestextParser();
        case 'po': return new PortableObjectParser();
        case 'json': return new JsonParser();

        default:
            throw new Error(`Unrecognized resource kind: ${translationFileKind}`);
    }
};