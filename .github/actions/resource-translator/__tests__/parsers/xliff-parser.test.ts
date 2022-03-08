import { findInXliff } from '../../src/file-formats/xliff-file';
import { XliffParser } from '../../src/parsers/xliff-parser';

const parser = new XliffParser();

test('XLIFF PARSER: correctly parses from string', async () => {
    const content = `<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="ja">
  <file id="f1" original="Graphic Example.psd">
    <skeleton href="Graphic Example.psd.skl"/>
    <unit id="1">
      <segment>
        <source>Quetzal</source>
        <target>Quetzal</target>
      </segment>
    </unit>
    <unit id="2">
      <segment>
        <source>An application to manipulate and process XLIFF documents</source>
        <target>XLIFF 文書を編集、または処理 するアプリケーションです。</target>
      </segment>
    </unit>
    <unit id="3">
      <segment>
        <source>XLIFF Data Manager</source>
        <target>XLIFF データ・マネージャ</target>
      </segment>
    </unit>
  </file>
</xliff>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();
    expect(findInXliff(file, 0, 'Quetzal')!.target[0])
        .toEqual('Quetzal');
    expect(findInXliff(file, 0, 'An application to manipulate and process XLIFF documents')!.target[0])
        .toEqual('XLIFF 文書を編集、または処理 するアプリケーションです。');
    expect(findInXliff(file, 0, 'XLIFF Data Manager')!.target[0])
        .toEqual('XLIFF データ・マネージャ');
});

test('XLIFF PARSER: correctly formats back as string', async () => {
    const content = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="ja">
  <file id="f1" original="Graphic Example.psd">
    <skeleton href="Graphic Example.psd.skl"/>
    <unit id="1">
      <segment>
        <source>Quetzal</source>
        <target>Quetzal</target>
      </segment>
    </unit>
    <unit id="2">
      <segment>
        <source>An application to manipulate and process XLIFF documents</source>
        <target>XLIFF 文書を編集、または処理 するアプリケーションです。</target>
      </segment>
    </unit>
    <unit id="3">
      <segment>
        <source>XLIFF Data Manager</source>
        <target>XLIFF データ・マネージャ</target>
      </segment>
    </unit>
  </file>
</xliff>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const fileFormatted = parser.toFileFormatted(file, "");
    expect(fileFormatted).toEqual(content);
});

test('XLIFF PARSER: correctly applies translations', async () => {
    const content = `<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="ja">
  <file id="f1" original="Graphic Example.psd">
    <skeleton href="Graphic Example.psd.skl"/>
    <unit id="1">
      <segment>
        <source>Quetzal</source>
        <target>Quetzal</target>
      </segment>
    </unit>
    <unit id="2">
      <segment>
        <source>An application to manipulate and process XLIFF documents</source>
        <target>XLIFF 文書を編集、または処理 するアプリケーションです。</target>
      </segment>
    </unit>
    <unit id="3">
      <segment>
        <source>XLIFF Data Manager</source>
        <target>XLIFF データ・マネージャ</target>
      </segment>
    </unit>
  </file>
</xliff>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const result = parser.applyTranslations(file, {
        '0::An application to manipulate and process XLIFF documents': 'Applying changes for testing.',
        '0::Quetzal': 'Wisconsin beer is best!',
        '0::XLIFF Data Manager': 'Who is in charge?'
    }, 'en')

    expect(result).toBeTruthy();
    expect(result.xliff.$.trgLang).toEqual('en');
    expect(findInXliff(result, 0, 'Quetzal')!.target[0])
        .toEqual('Wisconsin beer is best!');
    expect(findInXliff(result, 0, 'An application to manipulate and process XLIFF documents')!.target[0])
        .toEqual('Applying changes for testing.');
    expect(findInXliff(result, 0, 'XLIFF Data Manager')!.target[0])
        .toEqual('Who is in charge?');
});

test('XLIFF PARSER: correctly creates translatable text map', async () => {
    const content = `<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="ja">
  <file id="f1" original="Graphic Example.psd">
    <skeleton href="Graphic Example.psd.skl"/>
    <unit id="1">
      <segment>
        <source>Quetzal</source>
        <target>Quetzal</target>
      </segment>
    </unit>
    <unit id="2">
      <segment>
        <source>An application to manipulate and process XLIFF documents</source>
        <target>XLIFF 文書を編集、または処理 するアプリケーションです。</target>
      </segment>
    </unit>
    <unit id="3">
      <segment>
        <source>XLIFF Data Manager</source>
        <target>XLIFF データ・マネージャ</target>
      </segment>
    </unit>
  </file>
</xliff>`;

    const file = await parser.parseFrom(content);
    expect(file).toBeTruthy();

    const translatableTextMap = parser.toTranslatableTextMap(file);
    expect(translatableTextMap).toBeTruthy();
    expect(translatableTextMap.text.get('0::Quetzal')).toEqual('Quetzal');
    expect(translatableTextMap.text.get('0::An application to manipulate and process XLIFF documents'))
        .toEqual('An application to manipulate and process XLIFF documents');
    expect(translatableTextMap.text.get('0::XLIFF Data Manager'))
        .toEqual('XLIFF Data Manager');
});