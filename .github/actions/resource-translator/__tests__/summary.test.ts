import { Summary } from '../src/abstractions/summary';

test('SUMMARY: summary object correctly instantiates and calculates properties', () => {
    const summary = new Summary('es', [ 'en', 'fr', 'de' ]);

    expect(summary.totalFileCount).toEqual(0);
    expect(summary.totalTranslations).toEqual(0);

    summary.newFileCount = 3;
    summary.newFileTranslations = 15;
    summary.updatedFileCount = 5;
    summary.updatedFileTranslations = 20;

    expect(summary.totalFileCount).toEqual(8);
    expect(summary.totalTranslations).toEqual(35);
});

