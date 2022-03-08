export type TranslationFileKind =
    /**
     * XML-based standard `*.resx` file format.
     * For more information, see
     * https://docs.microsoft.com/dotnet/framework/resources/creating-resource-files-for-desktop-apps#resources-in-resx-files
    */
    'resx' |

    /**
     * XML-based `*.xliff` file format.
     * For more information, see https://en.wikipedia.org/wiki/XLIFF
    */
    'xliff' |

    /**
     * Each line represents a key-value-pair, with each key and value be an assignment statement, (i.e.; SomeKey=SomeValue).
    */
    'restext' |

    /**
     * Each line represents a key-value-pair, with each key and value be an assignment statement, (i.e.; SomeKey=SomeValue).
    */
    'ini' |

    /**
     * This might take awhile to support, as I'm not familiar with this
     * file format. I would ❤ for someone from the community to help out here.
    */
    'po' |

    /**
     * JSON file format.
     * Supports nested objects, e.g.
     * {
     *      "messages": {
     *          "foo": {
     *              "bar": "Hello!"
     *          }
     *      }
     * }
    */
    'json';