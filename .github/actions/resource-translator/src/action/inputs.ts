export interface Inputs {
    /**
     * Azure Cognitive Services Translator subscription key. Store as GitHub secret.
    */
    subscriptionKey: string;

    /**
     * Azure Cognitive Services Translator endpoint. Store as GitHub secret.
    */
    endpoint: string;

    /**
     * Azure Cognitive Services Translator subscription key. Store as GitHub secret.
     */
    sourceLocale: string;

    /**
     * Azure Cognitive Services Translator region. Store as GitHub secret.
     */
    region?: string;

    /**
     * An array of locales to translate to, i.e.; [ 'fr', 'de', 'es' ].
     */
    toLocales?: string[];
}
