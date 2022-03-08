import { TranslationFile } from "../file-formats/translation-file";
import { TranslatableTextMap } from "../abstractions/translatable-text-map";

/**
 * A translation file parser interface that defines common functionality for:
 * - Parsing raw file content into a well-known translation resource file.
 * - Converting a well-known translation resource file instance into its native file string representation.
*/
export interface TranslationFileParser {
    /**
     * Parses the file's raw content into the corresponding @type {TranslationFile}
     * @return {Promise<TranslationFile>}
    */
    parseFrom(fileContent: string): Promise<TranslationFile>,

    /**
     * Transforms the given @param {TranslationFile} instance into its native
     * file string representation.
     * @returns {string}
    */
    toFileFormatted(instance: TranslationFile, defaultValue: string): string

    /**
     * Applies the translations, mapping them appropriately to the
     * corresponding @type {TranslationFile} instance.
    */
    applyTranslations(
        instance: TranslationFile,
        translations: { [key: string]: string } | undefined,
        targetLocale?: string): TranslationFile;

    /**
     * Converts the given instance into a translatable text map for processing.
    */
    toTranslatableTextMap(instance: TranslationFile): TranslatableTextMap;
}