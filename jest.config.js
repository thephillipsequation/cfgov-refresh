module.exports = {
  verbose: false,
  transform: {
    '^.+\\.jsx?$': 'babel-jest',
    '^.+\\.hbs$': '<rootDir>/test/util/preprocessor-handlebars.js'
  },
  collectCoverage: true,
  collectCoverageFrom: [
    '<rootDir>/cfgov/unprocessed/**/*.js'
  ],
  coveragePathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/cfgov/unprocessed/apps/.+/node_modules/',
    '<rootDir>/cfgov/unprocessed/apps/.+/webpack-config\.js$',
    '<rootDir>/cfgov/unprocessed/js/routes/'
  ],
  coverageDirectory: '<rootDir>/test/unit_test_coverage',
  moduleNameMapper: {
    '^Templates(.*)$': '<rootDir>/cfgov/unprocessed/apps/owning-a-home/templates$1'
  }
};