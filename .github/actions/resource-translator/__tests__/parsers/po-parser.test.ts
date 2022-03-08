import { PortableObjectToken } from '../../src/file-formats/po-file';
import { PortableObjectParser } from '../../src/parsers/po-parser';

const parser = new PortableObjectParser();

test('PO PARSER: correctly parses from string', async () => {
    const content = `msgid "There is one item."
msgid_plural "There are {0} items."
msgstr[0] "Il y a un élément."
msgstr[1] "Il y a {0} éléments."`;

    const portableObject = await parser.parseFrom(content);
    expect(portableObject.tokens).toBeTruthy();

    const assertToken = (token: PortableObjectToken, expectedId: string, expectedValue: string) => {
        expect(token).toBeTruthy();
        expect(token.id).toEqual(expectedId);
        expect(token.value).toEqual(expectedValue);
    };

    assertToken(portableObject.tokens[0], 'msgid', '"There is one item."');
    assertToken(portableObject.tokens[1], 'msgid_plural', '"There are {0} items."');
    assertToken(portableObject.tokens[2], 'msgstr[0]', '"Il y a un élément."');
    assertToken(portableObject.tokens[3], 'msgstr[1]', '"Il y a {0} éléments."');
});

test('PO PARSER: correctly formats back as string', async () => {
    const content = `msgid "There is one item."
msgid_plural "There are {0} items."
msgstr[0] "Il y a un élément."
msgstr[1] "Il y a {0} éléments."`;

    const portableObject = await parser.parseFrom(content);
    expect(portableObject.tokens).toBeTruthy();

    const fileFormatted = parser.toFileFormatted(portableObject, "");
    expect(fileFormatted).toEqual(content);
});

test('PO PARSER: correctly applies translations', async () => {
    const content = `msgid "There is one item."
msgid_plural "There are {0} items."
msgstr[0] "Il y a un élément."
msgstr[1] "Il y a {0} éléments."`;

    const portableObject = await parser.parseFrom(content);
    expect(portableObject.tokens).toBeTruthy();

    const result = parser.applyTranslations(portableObject, {
        '"There is one item."': '"Does this work?"'
    })
    const assertToken = (token: PortableObjectToken, expectedId: string, expectedValue: string) => {
        expect(token).toBeTruthy();
        expect(token.id).toEqual(expectedId);
        expect(token.value).toEqual(expectedValue);
    };

    assertToken(result.tokens[0], 'msgid', '"There is one item."');
    assertToken(result.tokens[1], 'msgid_plural', '"There are {0} items."');
    assertToken(result.tokens[2], 'msgstr[0]', '"Does this work?"');
    assertToken(result.tokens[3], 'msgstr[1]', '"Il y a {0} éléments."');
});

test('PO PARSER: correctly creates translatable text map', async () => {
    const content = `msgid "There is one item."
msgid_plural "There are {0} items."
msgstr[0] "Il y a un élément."
msgstr[1] "Il y a {0} éléments."`;

    const portableObject = await parser.parseFrom(content);
    expect(portableObject.tokens).toBeTruthy();

    const translatableTextMap = parser.toTranslatableTextMap(portableObject);

    expect(translatableTextMap).toBeTruthy();
    expect(translatableTextMap.text.get('"There is one item."')).toEqual('"There is one item."');
    expect(translatableTextMap.text.get('"There are {0} items."')).toEqual('"There are {0} items."');
});