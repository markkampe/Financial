package simulation;

//FIX - generalize assets to include property
//costs (potentially deductable) and (non-income) taxes
//general revenue (same category as stg)

/**
 * simulated investment with its own distinct growth and return profile
 * 
 * @author markk
 */
public class Asset {
	public String name;			// name of this asset
	
	private Rate dividendFunction;
	private Rate interestFunction;
	private Rate shortGainsFunction;
	private Rate appreciationFunction;
	
	private Simulation sim;		// global parameters
	private int max_computed;	// last year for which values are computed
	
	private int assetValue[];		// computed or assigned values on 1/1
	private int assetBasis[];	// basis on 1/1
	private int dividends[];	// annual dividend yields
	private int interest[];		// annual interest payments
	private int shortGains[];	// annual short term gains distribution
	private int appreciation[];	// annual long term gains distribution
	private int additions[];	// contributions made during this year
	private int sales[];		// basis on those sales
	private int salesBasis[];	// repayment of principal
	
	public boolean reInvest;	// do we reinvest distributions
	
	public boolean debug;		// are we debugging this asset
	
	/**
	 * create a new asset object
	 * 
	 * @param name		name of this asset
	 * @param divFunct	dividend yield function
	 * @param intFunct	interest yield function
	 * @param stgFunct	short term gains function
	 * @param growFunct	appreciation function
	 * @param reinvest	are returns reinvested
	 * @param startYear	first year of simulation
	 * @param sim.numYears	number of years in simulation
	 */
	public Asset(	String assetName,
					Rate divFunct,	Rate intFunct, 
					Rate stgFunct,	Rate growFunct,
					Boolean reinvest,
					Simulation simparms ) {
		
		name = assetName;
		dividendFunction = divFunct;
		interestFunction= intFunct;
		shortGainsFunction = stgFunct;
		appreciationFunction = growFunct;
		sim = simparms;
		
		reInvest = reinvest;
		
		max_computed = sim.firstYear - 1;

		debug = false;
		
		assetValue = new int[sim.numYears];
		dividends = new int[sim.numYears];
		interest = new int[sim.numYears];
		shortGains = new int[sim.numYears];
		assetBasis = new int[sim.numYears];
		appreciation = new int[sim.numYears];
		additions = new int[sim.numYears];
		sales = new int[sim.numYears];
		salesBasis = new int[sim.numYears];
		
		// all expenses start out zero
		for( int i = 0; i < sim.numYears; i++ ) {
			assetValue[i] = 0;
			dividends[i] = 0;
			interest[i] = 0;
			shortGains[i] = 0;
			assetBasis[i] = 0;
			appreciation[i] = 0;
			additions[i] = 0;
			sales[i] = 0;
			salesBasis[i] = 0;
		}
	}
	
	/**
	 * set the gross income for a specified year
	 * 
	 * @param year	year for which expense is being set (typically starting year)
	 * @param value	value of investment on 1/1
	 * @param basis basis for investment on 1/1
	 */
	public void setValue( int year, int value, int basis ) {
		int thisX = sim.getYearX(year);
		
		assetValue[thisX] = value;
		assetBasis[thisX] = basis; 
	}
	
	/**
	 * specify sa;es for a particular year
	 * 
	 * @param year	year for which harvests are being set
	 * @param value	size of sales for this year
	 * @param basis basis for those sales
	 */
	public void sell( int year, int value, int basis ) {
		int thisX = sim.getYearX( year );
		
		sales[thisX] = value;
		salesBasis[thisX] = basis; 
	}
	
	/**
	 * specify sa;es for a particular year 
	 * (with default basis computation)
	 * 
	 * @param year	year for which harvests are being set
	 * @param value	size of sales for this year
	 */
	public void sell( int year, int value ) {
		int thisX = sim.getYearX( year );
		
		sales[thisX] += value;
		double basisFraction = (double) assetValue[thisX] / (double) assetBasis[thisX];
		salesBasis[thisX] = (int) (basisFraction * value); 
	}
	
	/**
	 * specify additions for a particular year
	 * 
	 * @param year	year for which additions are being made
	 * @param value	size of additions for this year
	 */
	public void buy( int year, int value ) {
		int thisX = sim.getYearX(year);
		
		additions[thisX] += value;
	}
	
	/**
	 * specify returns and appreciation for a specified year
	 * 
	 * @param year	year for which additions are being made
	 * @param interest paid during this year
	 * @param dividends paid during this year
	 * @param short term gains paid during this year
	 * @param unrealized gains for this year
	 */
	public void setReturns( int year, 
							int interestPaid, 
							int dividendPaid, 
							int stgPaid,
							int unrealizedGains ) {
		int thisX = sim.getYearX(year);
		
		interest[thisX] = interestPaid;
		dividends[thisX] = dividendPaid;
		shortGains[thisX] = stgPaid;
		appreciation[thisX] = unrealizedGains;
		if (year < sim.lastYear) {
			int newval = assetValue[thisX] + unrealizedGains;
			newval += additions[thisX] - sales[thisX];
			int newbasis = assetBasis[thisX];
			newbasis += additions[thisX] - salesBasis[thisX];
			if (reInvest) {
				newval += interestPaid + dividendPaid + stgPaid;
				newbasis += interestPaid + dividendPaid + stgPaid;
			}
			assetValue[thisX+1] = newval; 
			assetBasis[thisX+1] = newbasis;
		}
		max_computed = year;
	}
	
	/**
	 * return value of investment on 1/1 of specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		value of investment on 1/1 of specified year
	 */
	public int getValue( int year ) {
		int thisX = sim.getYearX(year);
		
		// we need up-to-date gains for the previous year
		if (year-1 > max_computed)
			compute( year-1 );
		
		return assetValue[thisX];
	}
	
	/**
	 * return asset basis on 1/1
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		asset basis on 1/1
	 */
	public int getBasis( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return assetBasis[thisX];
	}
	
	/**
	 * return interest paid by investment in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		interest paid during that year
	 */
	public int getInterest( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return interest[thisX];
	}
	
	/**
	 * return dividends paid by an investment in specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		dividends paid during that year
	 */
	public int getDividends( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return dividends[thisX];
	}
	
	/**
	 * return short term gains distributions paid by investment in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		short term gains distributions paid during that year
	 */
	public int getShortTerm( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return shortGains[thisX];
	}
	
	/**
	 * return sales proceeds for the year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		gross sales proceeds for year
	 */
	public int getSales( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return sales[thisX];
	}
	
	/**
	 * return taxable sales proceeds for the year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		taxable sales proceeds for year
	 */
	public int getTaxProfit( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return sales[thisX] - salesBasis[thisX];
	}
	
	/**
	 * return unrealized gains to investment in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		unrealized gains after end of that year
	 */
	public int getGrowth( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return appreciation[thisX];
	}
	
	/**
	 * return purchases for the year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		total purchases for year
	 */
	public int getPurchases( int year ) {
		int thisX = sim.getYearX(year);
		
		if (year > max_computed)
			compute( year );
		
		return additions[thisX];
	}
	
	/**
	 * string form of asset state for a specified year
	 * 
	 * @param year	desired year
	 * @return		XML representation of asset state
	 */
	public String toString( int year ) {
		sim.getYearX(year);
		if (year > max_computed)
			compute( year );
		
		// if this asset no longer has value, return null
		if (getValue(year) <= 0)
			return null;
		
		/*
		 * NOTE: I use get routines rather than directly accessing
		 *  	 the variables because the get routines may be 
		 *  	 over-loaded by sub-classes ... which might still
		 *  	 want to use this method.
		 */
		String result = "<asset ";
			result += String.format("name=\"%s\" ", name);
			result += String.format("year=\"%s\" ", year);
			result += String.format("value=\"$%d\" ", getValue(year));
			result += String.format("basis=\"$%d\" ", getBasis(year));
			result += String.format("int=\"$%d\" ", getInterest(year));
			result += String.format("div=\"$%d\" ", getDividends(year));
			result += String.format("dist=\"$%d\" ", getShortTerm(year));
			result += String.format("buy=\"$%d\" ", getPurchases(year));
			result += String.format("sell=\"$%d\" ", getSales(year));
			result += String.format("profit=\"$%d\" ", getTaxProfit(year));
			result += String.format("growth=\"$%d\" ", getGrowth(year));
		result += ">";
		return result;
	}
	public String toString() {
		return toString( max_computed );
	}
	
	/**
	 * apply various growth/yield functions to compute yields for given year
	 * <P>
	 * NOTE:This routine is only called if we have reason to believe
	 * 		that (at least) this year is not up-to-date.  Thus, we
	 * 		will force recomputation of the specified year, even if
	 * 		it has already been computed.  Perhaps harvests have changed.
	 * <P> 
	 * 		1/1 value must have already been set (by computation of the
	 * 		previous year)
	 *
	 * @param year	Year for which growth/yield is to be computed
	 */
	public void compute( int year ) {
		// validate the year
		sim.getYearX(year);
		
		// force reomputation of specified year
		if (max_computed >= year)
			max_computed = year - 1;
		
		// if we don't (yet) have a value for the specified year,
		//	  use the rate functions, additions, and harvests to compute
		//	  values from the last year for which we have values
		while( year > max_computed ) {
			// figure out the mean balance for the year
			int thisYear = max_computed + 1;
			int thisX = thisYear - sim.firstYear;
			int deltas = additions[thisX] - sales[thisX];
			int meanBal = assetValue[thisX] + deltas/2;
			
			// figure out the yields on this balance
			double earnedInt = (interestFunction == null) ? 0 : 
							meanBal * interestFunction.rateForYear( thisYear );
			double earnedDiv = (dividendFunction == null) ? 0 : 
							meanBal * dividendFunction.rateForYear( thisYear );
			double earnedStg = (shortGainsFunction == null) ? 0 :
							meanBal * shortGainsFunction.rateForYear( thisYear );
			double growth = (appreciationFunction == null) ? 0 : 
							meanBal * appreciationFunction.rateForYear( thisYear );
			setReturns(year, (int) earnedInt, (int) earnedDiv, 
					(int) earnedStg, (int) growth );
			
			if (debug) {
				System.out.println(toString(thisYear));
			}
		}
	}
}
