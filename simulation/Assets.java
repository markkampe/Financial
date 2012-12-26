package simulation;

import java.util.NoSuchElementException;

/**
 * a collection of assets.
 * <P>
 * The collection is, it-self, a pseudo-asset, but we also
 * expose the underlying collection to enable clients to
 * enumerate the set.
 * 
 * @author Mark
 */
public class Assets extends Asset {
	// perhaps I should make this dynamic some day
	private static final int MAX_ASSETS = 50;
	
	public Asset[] assets;
	public int numAssets;
	
	private int thisYear;
	
	/**
	 * allocate a set of expenses
	 */
	public Assets( String name, Simulation sim ) {
		super( name, null, null, null, null, false, sim );
		assets = new Asset[MAX_ASSETS];
		numAssets = 0;
		thisYear = 0;
	}
	
	/**
	 * update the composite pseudo-asset for the specified year
	 * 
	 * @param year
	 */
	private void update( int year ) {
		//usually, it is already up to date
		if (thisYear >= year)
			return;
		
		int value = 0;
		int basis = 0;
		int interest = 0;
		int dividends = 0;
		int shortTerm = 0;
		int growth = 0;
		int sales = 0;
		int profit = 0;
		int purchases = 0;
		
		for( int i = 0; i < numAssets; i++ ) {
			value += assets[i].getValue(year);
			basis += assets[i].getBasis(year);
			interest += assets[i].getInterest(year);
			dividends += assets[i].getDividends(year);
			shortTerm += assets[i].getShortTerm(year);
			growth += assets[i].getGrowth(year);
			sales += assets[i].getSales(year);
			profit += assets[i].getTaxProfit(year);
			purchases += assets[i].getPurchases(year);
		}
		
		// push all of these values to the aggregation asset
		super.setValue(year, value, basis );
		super.sell(year, sales, sales - profit);
		super.buy(year, purchases);
		super.setReturns( year, interest, dividends, shortTerm, growth );
		
		thisYear = year;
	}
	
	/**
	 * add a new asset to a collection of assets
	 * 
	 * @param asset		asset to add to collection			
	 * 
	 * @throws NoSuchElementException
	 */
	public void addAsset( Asset asset ) 
						throws NoSuchElementException {
		if (numAssets >= MAX_ASSETS)
			throw new NoSuchElementException("Too many assets");
		
		assets[numAssets] = asset;
		numAssets++;
	}
	
	/**
	 * return value of all investments on 1/1 of specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		value of investment on 1/1 of specified year
	 */
	public int getValue( int year ) {
		update( year );
		return super.getValue(year);
	}
	
	/**
	 * return interest paid by investments in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		interest paid during that year
	 */
	public int getInterest( int year ) {
		update( year );
		return super.getInterest(year);
	}
	
	/**
	 * return dividends paid by investments in specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		dividends paid during that year
	 */
	public int getDividends( int year ) {
		update(year);
		return super.getDividends(year);
	}
	
	/**
	 * return short term gains distributions paid investments in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		short term gains distributions paid during that year
	 */
	public int getShortTerm( int year ) {
		update(year);
		return super.getShortTerm(year);
	}
	
	/**
	 * return taxable profits from sales in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		taxable profits from sales during that year
	 */
	public int getTaxProfit( int year ) {
		update(year);
		return super.getTaxProfit(year);
	}
	/**
	 * return short term gains distributions paid investments in a specified year
	 * 
	 * @param year	for which value is desired
	 * 
	 * @return		short term gains distributions paid during that year
	 */
	public int getGrowth( int year ) {
		update(year);
		return super.getGrowth(year);
	}
	
	/**
	 * return a string form for the aggregate asset set
	 * 
	 * @param year
	 * @return
	 */
	public String toString( int year ) {
		update(year);
		return super.toString(year);
	}
}