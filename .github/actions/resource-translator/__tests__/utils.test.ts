import { dirname, resolve } from 'path';
import { DetectedLanguage, Result, TranslationResult } from '../src/abstractions/translation-results';
import { batch, chunk, getLocaleName, groupBy, stringifyMap, zip } from '../src/helpers/utils';

test("UTILS: group by functions correctly", () => {
    const cars = [
        { brand: 'Audi', color: 'black' },
        { brand: 'Ferrari', color: 'red' },
        { brand: 'Ford', color: 'white' },
        { brand: 'Toyota', color: 'white' },
        { brand: 'Audi', color: 'white' }
    ];

    const audiCars = groupBy(cars, 'brand');
    expect(audiCars).toEqual({
        'Audi': [
            { brand: 'Audi', color: 'black' },
            { brand: 'Audi', color: 'white' }
        ],
        'Ferrari': [
            { brand: 'Ferrari', color: 'red' }
        ],
        'Ford': [
            { brand: 'Ford', color: 'white' }
        ],
        'Toyota': [
            { brand: 'Toyota', color: 'white' }
        ]
    });
});

test('UTILS: group by functions correctly with translation results', () => {
    const result: TranslationResult = {
        detectedLanguage: {
            language: 'en',
            score: 1.0
        } as DetectedLanguage,
        translations: [
            { to: 'fr', text: 'salut comment allez-vous?' },
            { to: 'fr', text: 'Je vous remercie' },
            { to: 'es', text: 'Te deseo todo lo mejor' },
            { to: 'fr', text: `Jusqu'à notre prochaine rencontre, prenez soin de vous` },
            { to: 'bg', text: 'Сламен танц, дефтони!' }
        ] as Result[]
    };

    const grouped = groupBy(result.translations, 'to');
    expect(grouped).toEqual({
        'fr': [
            { to: 'fr', text: 'salut comment allez-vous?' },
            { to: 'fr', text: 'Je vous remercie' },
            { to: 'fr', text: `Jusqu'à notre prochaine rencontre, prenez soin de vous` }
        ],
        'es': [
            { to: 'es', text: 'Te deseo todo lo mejor' }
        ],
        'bg': [
            { to: 'bg', text: 'Сламен танц, дефтони!' }
        ]
    });
});

test('UTILS: get locale file name correctly swaps locale.', () => {
    const resourcePath = resolve(__dirname, "./data/Test.en.resx");
    const directory = dirname(resourcePath);
    const localePath = getLocaleName(resourcePath, 'fr');

    expect(localePath).toEqual(resolve(directory, 'Test.fr.resx'));
});

test('UTILS: JSON stringify map replacer.', () => {
    const map: Map<string, string> = new Map();
    map.set('1', 'one');
    map.set('2', 'two');

    const obj = {
        test: 'Sample',
        map
    };

    expect(JSON.stringify(obj, stringifyMap)).toEqual(`{"test":"Sample","map":{"dataType":"Map","value":[["1","one"],["2","two"]]}}`);
});

test('UTILS: Chunk array functions correctly.', () => {
    const abcs = ['a', 'b', 'c', 'd', 'e', 'f', 'g'];
    const chunks = chunk(abcs, 2);

    expect(chunks.length).toEqual(4);
    expect(chunks[0]).toEqual(['a', 'b']);
    expect(chunks[1]).toEqual(['c', 'd']);
    expect(chunks[2]).toEqual(['e', 'f']);
    expect(chunks[3]).toEqual(['g']);
});

test('UTILS: Zip arrays functions correctly.', () => {
    const abcs = ['a', 'b', 'c', 'd'];
    const nums = [1, 2, 3, 4];
    const zipped = zip(abcs, nums);

    expect(zipped.length).toBeTruthy();
    expect(zipped[0]).toEqual(['a', 1]);
    expect(zipped[1]).toEqual(['b', 2]);
    expect(zipped[2]).toEqual(['c', 3]);
    expect(zipped[3]).toEqual(['d', 4]);
});

test('UTILS: Batch array functions correctly.', () => {
    const array = ['a', 'bc', 'd', 'e', 'fg', 'h', 'i'];
    const batches = batch(array, 2, 7);

    expect(batches.length).toEqual(5);
    expect(batches[0]).toEqual(['a']);
    expect(batches[1]).toEqual(['bc']);
    expect(batches[2]).toEqual(['d', 'e']);
    expect(batches[3]).toEqual(['fg']);
    expect(batches[4]).toEqual(['h', 'i']);
});