import { debug } from '@actions/core';
import { context, getOctokit } from '@actions/github';
import { create } from '@actions/glob';
import { isDirectory } from '@actions/io/lib/io-util';
import { basename, normalize, resolve } from 'path';

export interface TranslationFileMap {
    ini?: string[] | undefined;
    po?: string[] | undefined;
    restext?: string[] | undefined;
    resx?: string[] | undefined;
    xliff?: string[] | undefined;
    json?: string[] | undefined;
}

const translationFileSchemes = {
    ini: (locale: string) => `**/*.${locale}.ini`,
    po: `**/*.po`,
    restext: (locale: string) => `**/*.${locale}.restext`,
    resx: (locale: string) => `**/*.${locale}.resx`,
    xliff: (locale: string) => `**/*.${locale}.xliff`,
    json: (locale: string) => `**/*.${locale}.json`
};

export async function findAllTranslationFiles(sourceLocale: string): Promise<TranslationFileMap> {
    const filesToInclude = await getFilesToInclude();
    const includeFile = (filepath: string) => {
        if (filesToInclude && filesToInclude.length > 0) {
            const filename = basename(filepath);
            const include = filesToInclude.some(f => f.toLowerCase() === filename.toLowerCase());
            debug(`include=${include}, ${filename}`);
            return include;
        }

        return true;
    };

    const patterns = Object.values(translationFileSchemes).map(fileScheme => {
        return "function" === typeof fileScheme ? fileScheme(sourceLocale) : fileScheme;
    });

    const globber = await create(patterns.join('\n'));
    const filesAndDirectories = await globber.glob();
    const promises = filesAndDirectories.map(async path => {
        return {
            path: normalize(path),
            isDirectory: await isDirectory(path),
            include: includeFile(path)
        };
    });
    const files = await Promise.all(promises);
    const results =
        files.filter(file => file.include && !file.isDirectory)
            .map(file => file.path);

    debug(`Files to translate:\n\t${results.join('\n\t')}`);

    return {
        po: results.filter(f => f.endsWith('.po')),
        restext: results.filter(f => f.endsWith('.restext')),
        ini: results.filter(f => f.endsWith('.ini')),
        resx: results.filter(f => f.endsWith('.resx')),
        xliff: results.filter(f => f.endsWith('.xliff')),
        json: results.filter(f => f.endsWith('.json'))
    };
}

async function getFilesToInclude(): Promise<string[]> {
    try {
        // Get all files related to trigger.
        const token = process.env['GITHUB_TOKEN'] || null;
        if (token) {
            const octokit = getOctokit(token);
            const options = {
                ...context.repo,
                ref: context.ref
            };
            debug(JSON.stringify(options));
            const response = await octokit.repos.getCommit(options);

            debug(JSON.stringify(response));

            if (response.data) {
                const files = [
                    ...new Set(response.data.files.map(file => {
                        const path = resolve(__dirname, file.filename);
                        return basename(path);
                    }))
                ];

                debug(`Files from trigger:\n\t${files.join('\n\t')}`);
                return files;
            }
        } else {
            debug("Unable to get the GITHUB_TOKEN from the environment.");
        }
    } catch (error) {
        debug(error);
    }

    return [];
}