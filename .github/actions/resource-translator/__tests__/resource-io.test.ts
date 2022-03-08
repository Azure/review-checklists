import { readFile, writeFile } from '../src/io/reader-writer';
import { resolve } from 'path';
import { getLocaleName } from '../src/helpers/utils';
import { ResxParser } from '../src/parsers/resx-parser';
import { TranslationFile } from '../src/file-formats/translation-file';

const parser = new ResxParser();

jest.useFakeTimers();

test('IO: read file correctly parses known XML', async () => {
    const resourcePath = resolve(__dirname, './data/Test.en.resx');
    const text = readFile(resourcePath);
    const resourceXml = await parser.parseFrom(text);

    expect(resourceXml).toBeTruthy();
    expect(resourceXml.root).toBeTruthy();
    expect(resourceXml.root.data).toBeTruthy();

    expect(resourceXml.root.data[0].$.name).toEqual('Greetings');
    expect(resourceXml.root.data[0].value[0]).toEqual('Hello world, this is a test.... only a test!');
    expect(resourceXml.root.data[1].$.name).toEqual('MyFriend');
    expect(resourceXml.root.data[1].value[0]).toEqual('Where have you gone?');
});

test('IO: roundtrip, resolve->read->write->read-> compare', async () => {
    const fakePath = resolve(__dirname, './test-7.en.resx');
    const resourcePath = resolve(__dirname, './data/Test.en.resx');
    const xml = readFile(resourcePath);
    const resourceXml = await parser.parseFrom(xml);

    writeFile(fakePath, xml);

    const compareXml = readFile(fakePath);
    expect(xml).toEqual(compareXml);

    expect(resourceXml).toBeTruthy();
    expect(resourceXml.root).toBeTruthy();
    expect(resourceXml.root.data).toBeTruthy();

    expect(resourceXml.root.data[0].$.name).toEqual('Greetings');
    expect(resourceXml.root.data[0].value[0]).toEqual('Hello world, this is a test.... only a test!');
    expect(resourceXml.root.data[1].$.name).toEqual('MyFriend');
    expect(resourceXml.root.data[1].value[0]).toEqual('Where have you gone?');
});

test('IO: apply translations to Sample.en.resx', async () => {
    const resourcePath = resolve(__dirname, './data/Sample.en.resx');
    const xml = readFile(resourcePath);
    let parsedFile = await parser.parseFrom(xml);

    const resultSet = {
        "es": {
            "FamilyDescription": "Cadena de muestra para probar la traducción"
        }
    };

    ['es'].forEach(locale => {
        const translations = resultSet[locale];
        if (!translations) {
            return;
        }

        const clone = Object.assign({} as TranslationFile, parsedFile);
        const result =
            parser.applyTranslations(clone, translations);

        expect(result).toBeTruthy();
        expect(result.root).toBeTruthy();
        expect(result.root.data).toBeTruthy();

        expect(result.root.data[0].$.name).toEqual('FamilyDescription');
        expect(result.root.data[0].value[0]).toEqual('Cadena de muestra para probar la traducción');
    });
});

test('IO: apply translations to Test.en.resx', async () => {
    const resourcePath = resolve(__dirname, './data/Test.en.resx');
    const xml = readFile(resourcePath);
    let resourceXml = await parser.parseFrom(xml);

    const fakeResults = {
        'MyFriend': 'We meet again!',
        'Greetings': 'This is a fake translation'
    };

    resourceXml = parser.applyTranslations(resourceXml, fakeResults);

    expect(resourceXml).toBeTruthy();
    expect(resourceXml.root).toBeTruthy();
    expect(resourceXml.root.data).toBeTruthy();

    expect(resourceXml.root.data[0].$.name).toEqual('Greetings');
    expect(resourceXml.root.data[0].value[0]).toEqual('This is a fake translation');
    expect(resourceXml.root.data[1].$.name).toEqual('MyFriend');
    expect(resourceXml.root.data[1].value[0]).toEqual('We meet again!');
});

test('IO: apply translations to Index.en.resx', async () => {
    const resourcePath = resolve(__dirname, './data/Index.en.resx');
    const xml = readFile(resourcePath);
    let resourceXml = await parser.parseFrom(xml);

    const fakeResults = {
        'HelloWorld': 'Goodbye my friend',
        'Greeting': 'From around the world.',
        'SurveyTitle': 'I do not like surveys!'
    };

    resourceXml = parser.applyTranslations(resourceXml, fakeResults);

    expect(resourceXml).toBeTruthy();
    expect(resourceXml.root).toBeTruthy();
    expect(resourceXml.root.data).toBeTruthy();

    expect(resourceXml.root.data[0].$.name).toEqual('Greeting');
    expect(resourceXml.root.data[0].value[0]).toEqual('From around the world.');
    expect(resourceXml.root.data[1].$.name).toEqual('HelloWorld');
    expect(resourceXml.root.data[1].value[0]).toEqual('Goodbye my friend');
    expect(resourceXml.root.data[2].$.name).toEqual('SurveyTitle');
    expect(resourceXml.root.data[2].value[0]).toEqual('I do not like surveys!');
});

test('IO: correctly gets local name.', () => {
    const resourcePath = resolve(__dirname, './data/Index.en.resx');
    const localName = getLocaleName(resourcePath, 'fr');

    expect(localName).toEqual(resourcePath.replace('.en.resx', '.fr.resx'));
})