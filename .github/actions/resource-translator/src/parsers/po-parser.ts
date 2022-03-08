import { PortableObjectFile, PortableObjectToken } from "../file-formats/po-file";
import { TranslationFileParser } from "./translation-file-parser";
import { TranslatableTextMap } from "../abstractions/translatable-text-map";
import { delay, findNext } from "../helpers/utils";

export class PortableObjectParser implements TranslationFileParser {
    async parseFrom(fileContent: string): Promise<PortableObjectFile> {
        await delay(0, null);
        let portableObjectFile: PortableObjectFile = {
            tokens: []
        };
        if (fileContent) {
            portableObjectFile.tokens =
                fileContent.split('\n').map(
                    line => new PortableObjectToken(line));
        }
        return portableObjectFile;
    }

    toFileFormatted(instance: PortableObjectFile, defaultValue: string): string {
        return !!instance ? instance.tokens.map(t => t.line).join('\n') : defaultValue;
    }

    applyTranslations(
        portableObject: PortableObjectFile,
        translations: { [key: string]: string; } | undefined,
        targetLocale?: string): PortableObjectFile {
        if (portableObject && translations) {
            let lastIndex = 0;
            for (let key in translations) {
                const value = translations[key];
                if (value) {
                    lastIndex = findNext(
                        portableObject.tokens,
                        lastIndex,
                        token => {
                            let foundFirst = false;
                            let secondOffset = 0;
                            if (!token.isInsignificant) {
                                if (token.value === key) {
                                    foundFirst = true;
                                    secondOffset = token.id === 'msgid' ? 0 : 1;
                                }
                            }
                            return [foundFirst, secondOffset];
                        },
                        (token, secondOffset) => {
                            let foundSecond = false;
                            if (!token.isInsignificant) {
                                foundSecond = secondOffset
                                    ? token.id!.startsWith(`msgstr[${secondOffset}]`)
                                    : token.id!.startsWith('msgstr');
                            }
                            return foundSecond;
                        },
                        token => token.value = value);
                }
            }
        }

        return portableObject;
    }

    toTranslatableTextMap(instance: PortableObjectFile): TranslatableTextMap {
        const textToTranslate: Map<string, string> = new Map();
        const tokens = instance.tokens;
        if (tokens && tokens.length) {
            tokens.forEach(token => {
                if (token.isCommentLine || token.isInsignificant || !token.value) {
                    return;
                }

                if (token.id === 'msgid' || token.id === 'msgid_plural') {
                    textToTranslate.set(token.value, token.value);
                }
            });
        }

        return {
            text: textToTranslate
        };
    }
}