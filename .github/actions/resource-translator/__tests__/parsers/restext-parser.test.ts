import { RestextParser } from '../../src/parsers/restext-parser';

const parser = new RestextParser();

test('RESTEXT PARSER: correctly parses from string', async () => {
    const content = `; Title section
[Title Section]
Title=Title Casing For The Win

; General section
[General strings, etc]
Strings=This is the first string, in a series of several.
Message=Button is clicked!`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();
    expect(file['Title']).toEqual('Title Casing For The Win');
    expect(file['Strings']).toEqual('This is the first string, in a series of several.');
    expect(file['Message']).toEqual('Button is clicked!');
});

test('RESTEXT PARSER: correctly formats back as string', async () => {
    const content = `; Title section
[Title Section]
Title=Title Casing For The Win

; General section
[General strings, etc]
Strings=This is the first string, in a series of several.
Message=Button is clicked!`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const fileFormatted = parser.toFileFormatted(file, "");
    expect(fileFormatted).toEqual(content);
});

test('RESTEXT PARSER: correctly applies translations', async () => {
    const content = `; Title section
[Title Section]
Title=Title Casing For The Win

; General section
[General strings, etc]
Strings=This is the first string, in a series of several.
Message=Button is clicked!`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const result = parser.applyTranslations(file, {
        'Strings': 'Does this work?'
    })

    expect(result).toBeTruthy();
    expect(result['Title']).toEqual('Title Casing For The Win');
    expect(result['Strings']).toEqual('Does this work?');
    expect(result['Message']).toEqual('Button is clicked!');
});

test('RESTEXT PARSER: correctly creates translatable text map', async () => {
    const content = `; Title section
[Title Section]
Title=Title Casing For The Win

; General section
[General strings, etc]
Strings=This is the first string, in a series of several.
Message=Button is clicked!`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const translatableTextMap = parser.toTranslatableTextMap(file);
    expect(translatableTextMap).toBeTruthy();
    expect(translatableTextMap.text.get('Title')).toEqual('Title Casing For The Win');
    expect(translatableTextMap.text.get('Strings')).toEqual('This is the first string, in a series of several.');
    expect(translatableTextMap.text.get('Message')).toEqual('Button is clicked!');
});