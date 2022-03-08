import { debug } from "@actions/core";
import { Summary } from "../abstractions/summary";

/**
 * Example output: https://gist.github.com/IEvangelist/8e7101bda2bacce98d418b5d0fdda756
 * @param summary The object representing the summary of the action's execution.
 */
export const summarize = (summary: Summary): [string, string] => {
    const fileCount = summary.totalFileCount.toLocaleString('en');
    const translations = summary.totalTranslations.toLocaleString('en');
    const title = `Machine-translated ${fileCount} files, a total of ${translations} translations`;

    const env = process.env;
    const server = env['GITHUB_SERVER_URL'];
    const repo = env['GITHUB_REPOSITORY'];
    const commit = env['GITHUB_SHA'];

    const triggeredByUrl = `${server}/${repo}/commit/${commit}`;

    const nfc = summary.newFileCount.toLocaleString('en');
    const nft = summary.newFileTranslations.toLocaleString('en');

    const ufc = summary.updatedFileCount.toLocaleString('en');
    const uft = summary.updatedFileTranslations.toLocaleString('en');

    // Pull request message template
    let details: string[] = [
        '# Translation pull request summary',
        '',
        `Action triggered by ${triggeredByUrl}.`,
        '',
        `- Source locale: \`${summary.sourceLocale}\``,
        `- Destination locale(s): ${summary.toLocales.map(locale => `\`${locale}\``).join(', ')}`,
        '',
        '## File translation details',
        '',
        '| Type    | File count | Translation count |',
        '|---------|------------|-------------------|',
        `| New     | ${nfc}     | ${nft}            |`,
        `| Updated | ${ufc}     | ${uft}            |`,
        '',
        `Of the ${fileCount} translated files, there are a total of ${translations} individual translations.`,
        '',
        '> These machine translations are a result of Azure Cognitive Services Translator, and the [Machine Translator](https://github.com/marketplace/actions/resource-translator) GitHub action. For more information, see [Translator v3.0](https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-reference?WT.mc_id=dapine). To post an issue, or feature request please do so [here](https://github.com/IEvangelist/resource-translator/issues).',
    ];

    debug(JSON.stringify({
        title,
        details
    }));

    return [title, details.join('\n')];
}