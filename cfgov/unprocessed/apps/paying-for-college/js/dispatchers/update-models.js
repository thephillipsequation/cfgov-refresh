/**
 * Update the values of models
 */

import { expensesModel } from '../models/expenses-model.js';
import { financialModel } from '../models/financial-model.js';
import { financialView } from '../views/financial-view.js';
import { schoolModel } from '../models/school-model.js';
import { getSchoolData } from '../dispatchers/get-api-values.js';

/**
  * updateFinancial - Update a property of the financial model
  * @param {String} name - The name of the property to update
  * @param {} value - The new value of the property
  */

const updateFinancial = function( name, value ) {
  financialModel.setValue( name, value );
};

const createFinancial = function( name, value ) {
  financialModel.createFinancialProperty( name, value );
};

const updateSchoolData = function( iped ) {
  getSchoolData( iped )
    .then( resp => {
      const data = JSON.parse( resp.responseText );

      for ( const key in data ) {
        schoolModel.createSchoolProperty( key, data[key] );
      }

      financialModel.addSchoolAndConstants();
      financialView.updateFinancialItems();

    } );
}

export {
  updateFinancial,
  createFinancial,
  updateSchoolData
};
