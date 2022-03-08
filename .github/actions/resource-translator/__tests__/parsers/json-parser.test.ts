import { JsonParser } from '../../src/parsers/json-parser';

const parser = new JsonParser();

const content = JSON.stringify(
    {
        messages: {
            bar: "John",
            foo: {
                msg1: "hello {{variable}}",
                msg2: "world"
            },
        },
        msg3: "Doe",
        "msg.4": "this is a fullstop.",
        "msg.5.": "this is a fullstop. With another sentance."
    }, null, '\t');

test('JSON PARSER: correctly parses from string', async () => {
    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();
    expect(file[`messages${JsonParser.DELIMITER}foo${JsonParser.DELIMITER}msg1`]).toEqual('hello {{variable}}');
    expect(file[`messages${JsonParser.DELIMITER}foo${JsonParser.DELIMITER}msg2`]).toEqual('world');
    expect(file[`messages${JsonParser.DELIMITER}bar`]).toEqual('John');
    expect(file['msg3']).toEqual('Doe');
    expect(file['msg.4']).toEqual('this is a fullstop.');
    expect(file['msg.5.']).toEqual('this is a fullstop. With another sentance.');
});

test('JSON PARSER: correctly formats back as string', async () => {
    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const fileFormatted = parser.toFileFormatted(file, "");
    expect(fileFormatted).toEqual(content);
});

test('JSON PARSER: correctly applies translations', async () => {
    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const result = parser.applyTranslations(file, {
        'messages[--]foo[--]msg2': 'Does this work?'
    });

    expect(result).toBeTruthy();
    expect(file[`messages${JsonParser.DELIMITER}foo${JsonParser.DELIMITER}msg1`]).toEqual('hello {{variable}}');
    expect(file[`messages${JsonParser.DELIMITER}foo${JsonParser.DELIMITER}msg2`]).toEqual('Does this work?');
    expect(file[`messages${JsonParser.DELIMITER}bar`]).toEqual('John');
    expect(file['msg3']).toEqual('Doe');
    expect(file['msg.4']).toEqual('this is a fullstop.');
    expect(file['msg.5.']).toEqual('this is a fullstop. With another sentance.');
});

test('JSON PARSER: correctly creates translatable text map', async () => {
    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const translatableTextMap = parser.toTranslatableTextMap(file);
    expect(translatableTextMap).toBeTruthy();
    expect(translatableTextMap.text.get(`messages${JsonParser.DELIMITER}foo${JsonParser.DELIMITER}msg1`)).toEqual('hello {{variable}}');
    expect(translatableTextMap.text.get(`messages${JsonParser.DELIMITER}foo${JsonParser.DELIMITER}msg2`)).toEqual('world');
    expect(translatableTextMap.text.get(`messages${JsonParser.DELIMITER}bar`)).toEqual('John');
    expect(translatableTextMap.text.get('msg3')).toEqual('Doe');
    expect(translatableTextMap.text.get('msg.4')).toEqual('this is a fullstop.');
    expect(translatableTextMap.text.get('msg.5.')).toEqual('this is a fullstop. With another sentance.');
});