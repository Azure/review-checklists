import { ResxParser } from '../../src/parsers/resx-parser';

const parser = new ResxParser();

test('RESX PARSER: correctly parses from string', async () => {
    const content = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<root>
  <data name="Greetings" xml:space="preserve">
    <value>Hello world, this is a test.... only a test!</value>
  </data>
  <data name="MyFriend" xml:space="preserve">
    <value>Where have you gone?</value>
  </data>
</root>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();
    expect(file.root.data.find(d => d.$.name === 'Greetings')!.value[0]).toEqual('Hello world, this is a test.... only a test!');
    expect(file.root.data.find(d => d.$.name === 'MyFriend')!.value[0]).toEqual('Where have you gone?');
});

test('RESX PARSER: correctly formats back as string', async () => {
    const content = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<root>
  <data name="Greetings" xml:space="preserve">
    <value>Hello world, this is a test.... only a test!</value>
  </data>
  <data name="MyFriend" xml:space="preserve">
    <value>Where have you gone?</value>
  </data>
</root>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const fileFormatted = parser.toFileFormatted(file, "");
    expect(fileFormatted).toEqual(content);
});

test('RESX PARSER: correctly applies translations', async () => {
    const content = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<root>
  <data name="Greetings" xml:space="preserve">
    <value>Hello world, this is a test.... only a test!</value>
  </data>
  <data name="MyFriend" xml:space="preserve">
    <value>Where have you gone?</value>
  </data>
</root>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const result = parser.applyTranslations(file, {
        'Greetings': 'I am a robot!'
    })

    expect(result).toBeTruthy();
    expect(result.root.data.find(d => d.$.name === 'Greetings')!.value[0]).toEqual('I am a robot!');
    expect(result.root.data.find(d => d.$.name === 'MyFriend')!.value[0]).toEqual('Where have you gone?');
});

test('RESX PARSER: correctly creates translatable text map', async () => {
    const content = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<root>
  <data name="Greetings" xml:space="preserve">
    <value>Hello world, this is a test.... only a test!</value>
  </data>
  <data name="MyFriend" xml:space="preserve">
    <value>Where have you gone?</value>
  </data>
</root>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const translatableTextMap = parser.toTranslatableTextMap(file);
    expect(translatableTextMap).toBeTruthy();
    expect(translatableTextMap.text.get('Greetings')).toEqual('Hello world, this is a test.... only a test!');
    expect(translatableTextMap.text.get('MyFriend')).toEqual('Where have you gone?');
});