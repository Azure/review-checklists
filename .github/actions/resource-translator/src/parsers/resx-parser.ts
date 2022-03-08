import { Data, ResourceFile, traverseResx } from '../file-formats/resource-file';
import { TranslationFileParser } from './translation-file-parser';
import { XmlFileParser } from './xml-file-parser';

export class ResxParser implements TranslationFileParser {
    async parseFrom(fileContent: string): Promise<ResourceFile> {
        return await XmlFileParser.fromXml<ResourceFile>(fileContent);
    }

    toFileFormatted(instance: ResourceFile, defaultValue: string): string {
        try {
            return XmlFileParser.toXml(instance);
        } catch (error) {
            return defaultValue;
        }
    }

    applyTranslations(
        resource: ResourceFile,
        translations: { [key: string]: string } | undefined,
        targetLocale?: string) {
        if (resource && translations) {
            for (let key in translations) {
                const value = translations[key];
                if (value) {
                    traverseResx(resource, key, (data: Data)  => data.value = [value]);
                }
            }
        }

        return resource;
    }

    toTranslatableTextMap(instance: ResourceFile) {
        const textToTranslate: Map<string, string> = new Map();
        const values = instance.root.data;
        if (values && values.length) {
            for (let i = 0; i < values.length; ++i) {
                const key = values[i].$.name;
                const value = values[i].value![0];

                textToTranslate.set(key, value);
            }
        }

        return {
            text: textToTranslate
        };
    }
}