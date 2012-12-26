package simulation;

import java.util.NoSuchElementException;
/**
 * real property with (appreciating/depreciating) value, 
 * taxes, and insurance
 * 
 * @author Mark
 */
public class Property {
	private String name;		// name of this property
	private String subClass;	// type of property
	
	private Simulation sim;		// global simulation parameters
	
	private int marketValue[];	// market value on 1/1 of each year
	private int assessedValue[];// assessed value on 1/1 of each yearB
	private int taxBasis[];		// tax basis for this property
	private int deltaMkt[];		// market value of improvements
	private int deltaAss[];		// assessed value of improvements
	private int deltaCost[];	// actual cost of improvements
	private int max_computed;	// maximum year for which value is calculated
	
	private Rate valueFunc;		// market value appreciation/depreciation function
	private Rate assessFunc;	// assessed value appreciation function
	private TaxRates insFunc;	// insurance rate computation schedule
	private TaxRates taxFunc;	// property tax rate computation schedule
	
	public boolean debug;		// enable debugging for this property
	
	/**
	 * Create a new property, with specified value/tax/insurance functions
	 * <P>
	 * NOTE: property insurance rates are computed as a propterty
	 * 		 tax, based on a marginal tax rate schedule.  This will
	 * 		 normally be way-over-kill, but we already have the mechanism.
	 * @param subclass			type of property
	 * @param appreciationFunc	appreciation/depreciation rates
	 * @param insuranceRates	insurance (tax) function
	 * @param taxRates			property tax function
	 * @param name				name of this property
	 * @param assessFunction	assessed value change rates
	 * 
	 * @param siml.startYear			first year of simulation
	 * @param sim.numYears			number of years in simulation
	 */
	public Property( String propertyName,
					String subclass,
					Rate appreciationFunc,
					Rate assessmentFunc,
					TaxRates insuranceRates,
					TaxRates taxRates, Simulation simParms
					) {
		
		name = propertyName;
		subClass = subclass;
		sim = simParms;
		max_computed = sim.firstYear;
		
		valueFunc = appreciationFunc;
		assessFunc = assessmentFunc;
		insFunc = insuranceRates;
		taxFunc = taxRates;
		
		marketValue = new int[sim.numYears];
		assessedValue = new int[sim.numYears];
		taxBasis = new int[sim.numYears];
		deltaMkt = new int[sim.numYears];
		deltaAss = new int[sim.numYears];
		deltaCost = new int[sim.numYears];
		
		for( int i = 0; i < sim.numYears; i++) {
			marketValue[i] = 0;
			assessedValue[i] = 0;
			taxBasis[i] = 0;
			deltaMkt[i] = 0;
			deltaAss[i] = 0;
			deltaCost[i] = 0;
		}
		
		debug = false;
	}

	/**
	 * set the value of the property in a particular year
	 * 
	 * NOTE:	this operation has the side-effect of computing
	 * 			the value for all preceding years ... so values
	 * 			should be set in chronological order.
	 * 
	 * @param year			year of valuation
	 * @param market	valuation in that year
	 * @param assessed	valuation for that year
	 * @param basis		tax basis in that year
	 */
	public void setValue( int year, int market, int assessed, int basis ) 
			throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// calculate all the intervening years
		if (max_computed < year)
			compute( year );
		
		marketValue[thisX] = market;
		assessedValue[thisX] = assessed;
		taxBasis[thisX] = basis;
	}	
	
	/**
	 * record an improvement (or discrete depreciation event)
	 * 
	 *  NOTE:	this operation has the side-effect of computing
	 * 			the value for all preceding years ... so these
	 * 			should be recorded in chronological order.
	 * 
	 * @param year		year of event
	 * @param cost		cost basis of improvements
	 * @param cost		actual cost of improvements
	 * @param market	amount of market value change (+ appreciation)
	 * @param assessed	amount of assessed value change
	 * 
	 * @throws NoSuchElementException	if year is out of range
	 */
	public void improve( int year, int cost, int market, int assessed ) 
			throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// calculate up to this year
		if (max_computed < year)
			compute( year );
		
		deltaMkt[thisX] += market;
		deltaAss[thisX] += assessed;
		deltaCost[thisX] += cost;
	}
	
	/**
	 * return the market value of the property in a specified year
	 * 
	 * @param year	year of desired valuation
	 * @return		appreciated/improved value in that year
	 * @throws NoSuchElementException	if year is out of range
	 */
	public int getValue( int year ) throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// make sure we have a value for this year
		if (max_computed < year)
			compute( year );
		
		return marketValue[thisX];
	}
	
	/**
	 * return the assessed value of the property in a specified year
	 * 
	 * @param year	year of desired valuation
	 * @return		appreciated/improved value in that year
	 * @throws NoSuchElementException	if year is out of range
	 */
	public int getAssessed( int year ) throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// make sure we have a value for this year
		if (max_computed < year)
			compute( year );
		
		return assessedValue[thisX];
	}
	
	/**
	 * return the tax basis of the property in a specified year
	 * 
	 * @param year	year of desired valuation
	 * @return		appreciated/improved value in that year
	 * @throws NoSuchElementException	if year is out of range
	 */
	public int getBasis( int year ) throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// make sure we have a value for this year
		if (max_computed < year)
			compute( year );
		
		return taxBasis[thisX];
	}
	
	/**
	 * return the improvements made in a specified year
	 * 
	 * @param year	year of desired valuation
	 * @return		improvments made during that year
	 */
	public int getImprovements( int year ) {
		int thisX = sim.getYearX(year);
		
		// make sure we have a value for this year
		if (max_computed < year)
			compute( year );
		
		return deltaCost[thisX];
	}
	
	
	
	/**
	 * return the insurance cost for a specified year
	 * 
	 * @param year	year for which insurance should be returned
	 * @return		insurance cost for that year
	 * 
	 * @throws NoSuchElementException	if year is out of range
	 */
	public int getInsurance( int year ) throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// make sure we have a value for this year
		if (max_computed < year)
			compute( year );
		
		return insFunc.taxOn( year, marketValue[thisX]);
	}
	
	/**
	 * return the property tax for a specified year
	 * 
	 * @param year	year for which tax should be returned
	 * @return		insurance cost for that year
	 * 
	 * @throws NoSuchElementException	if year is out of range
	 */
	public int getTax( int year ) throws NoSuchElementException {
		int thisX = sim.getYearX(year);
		
		// make sure we have a value for this year
		if (max_computed < year)
			compute( year );
		
		return taxFunc.taxOn( year, assessedValue[thisX]);
	}
	
	/**
	 * compute the appreciated/depreciated value of the
	 * property for a given year.
	 * 
	 * NOTE:	this function should never be called for
	 * 			a year for which an explicit set/add has
	 * 			been done.
	 * 
	 * @param year	how far into future to compute values
	 */
	private void compute( int year ) {
		while( max_computed < year ) {
			int prevX = max_computed - sim.firstYear;
			
			// compute basis for this year
			taxBasis[prevX+1] = taxBasis[prevX] + deltaCost[prevX];
			
			// compute market value for this year
			double val = marketValue[prevX];
			if (valueFunc != null) {
				double appreciation = 1 + valueFunc.rateForYear(max_computed);
				val *= appreciation;
			}
			marketValue[prevX+1] = (int) val + deltaMkt[prevX];
			
			// compute assessed value for this year
			val = assessedValue[prevX];
			if (assessFunc != null) {
				double appreciation = 1 + assessFunc.rateForYear(max_computed);
				val *= appreciation;
			}
			
			assessedValue[prevX+1] = (int) val + deltaAss[prevX];
			max_computed++;
		}
	}
	
	/**
	 * string form of property state for a specified year
	 * 
	 * @param year	desired year
	 * @return		XML representation of state
	 */
	public String toString( int year ) {
		sim.getYearX(year);
		if (year > max_computed)
			compute( year );
		
		/*
		 * NOTE: I use get routines rather than directly accessing
		 *  	 the variables because the get routines may be 
		 *  	 over-loaded by sub-classes ... which might still
		 *  	 want to use this method.
		 */
		String result = "<property ";
			result += String.format("name=\"%s\" ", name);
			result += String.format("subclass=\"%s\" ", subClass);
			result += String.format("year=\"%s\" ", year);
			result += String.format("value=\"$%d\" ", getValue(year));
			result += String.format("basis=\"$%d\" ", getTax(year));
			result += String.format("assess=\"$%d\" ", getAssessed(year));
			result += String.format("tax=\"$%d\" ", getTax(year));
			result += String.format("ins=\"$%d\" ", getInsurance(year));
			result += String.format("improvements=\"$%d\" ", getImprovements(year));
		result += ">";
		return result;
	}
	public String toString() {
		return toString( max_computed );
	}
}