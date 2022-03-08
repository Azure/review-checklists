import { readFile } from '../src/io/reader-writer';
import { resolve } from 'path';
import { ResourceFile } from '../src/file-formats/resource-file';
import { ResxParser } from '../src/parsers/resx-parser';

let resourceFile: ResourceFile;
const parser = new ResxParser();

beforeEach(async () => {
    const resourcePath = resolve(__dirname, "./data/Test.en.resx");
    const text = readFile(resourcePath);
    resourceFile = await parser.parseFrom(text);
});

test("IO: translatable XML is mapped parses known XML", async () => {
    if (resourceFile !== null) {
        expect(resourceFile).toBeTruthy();

        const map = parser.toTranslatableTextMap(resourceFile).text;
        if (map !== null) {
            expect(map.get("Greetings")).toEqual("Hello world, this is a test.... only a test!");
            expect(map.get("MyFriend")).toEqual("Where have you gone?");
        }
    }
});

test('IO: get translatable text map', async () => {
    const resourcePath = resolve(__dirname, './data/Index.en.resx');
    const text = readFile(resourcePath);
    const file = await parser.parseFrom(text);
    const translatableTextMap = parser.toTranslatableTextMap(file);

    expect(translatableTextMap).toBeTruthy();
    expect(translatableTextMap.text).toBeTruthy();

    expect(translatableTextMap.text.get('Greeting')).toEqual('Welcome to your new app.');
    expect(translatableTextMap.text.get('HelloWorld')).toEqual('Hello, world!');
    expect(translatableTextMap.text.get('SurveyTitle')).toEqual('How is Blazor working for you?.');
});