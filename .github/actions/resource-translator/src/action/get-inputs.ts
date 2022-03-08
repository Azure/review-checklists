import { getInput } from '@actions/core';
import { Inputs } from './inputs';

export const getInputs = (): Inputs => {
    const inputs: Inputs = {
        subscriptionKey: getInput('subscriptionKey', { required: true }),
        endpoint: getInput('endpoint', { required: true }),
        sourceLocale: getInput('sourceLocale', { required: true }),
        region: getInput('region'),
        toLocales: getQuestionableArray('toLocales')
    };

    return inputs;
};

/**
 * Valid formats for parsing string into JS array:
 *   "'es','de','fr'"
 *   "[ 'es', 'de', 'fr' ]"
*/
export const getQuestionableArray = (inputName: string): string[] | undefined => {
    const value = getInput(inputName);
    if (value) {
        if (value.indexOf('[') > -1) {
            return [...JSON.parse(value)];
        } else {
            return value.replace(/\s/g, '').split(',')
        }
    }

    return undefined;
}