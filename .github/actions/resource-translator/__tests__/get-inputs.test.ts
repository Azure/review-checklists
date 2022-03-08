import { InputOptions } from '@actions/core';
import { getQuestionableArray } from '../src/action/get-inputs';

jest.mock('@actions/core', () => ({
    getInput: (name: string, options?: InputOptions) => {
        switch (name) {
            case 'stringValue': return 'es,de,fr';
            case 'arrayValue': return '[ "es", "de", "fr" ]';

            default: return '';
        }
    }
}));

test('GET INPUTS: returns undefined when null, empty, or invalid', () => {
    expect(getQuestionableArray('')).toBeFalsy();
});

test('GET INPUTS: returns valid array instance when string', () => {
    expect(getQuestionableArray('stringValue')).toEqual(["es", "de", "fr"]);
});

test('GET INPUTS: returns valid array instance when JSON array', () => {
    expect(getQuestionableArray('arrayValue')).toEqual(["es", "de", "fr"]);
});