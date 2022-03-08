import { debug } from '@actions/core';
import { readFileSync, writeFileSync } from 'fs';
import { resolve } from 'path';

export function readFile(path: string) {
    const resolved = resolve(path);
    const file = readFileSync(resolved, 'utf-8');

    debug(`Read file: ${file}`);
    
    return file;
}

export function writeFile(path: string, content: string) {
    debug(`Write file, path: ${path}\nContent: ${content}`)

    writeFileSync(path, content);
}