package simulation;

import java.util.NoSuchElementException;

/**
 * a collection of income sources.
 * 
 * because these are simply containers for groups of inomes,
 * we expose the array of sources
 * 
 * @author Mark
 */
public class Incomes extends Income {
	// perhaps I should make this dynamic some day
	private static final int MAX_SOURCES = 50;

	public Income sources[];
	public int numSources;
	
	private int max_calculated;

	/**
	 * allocate a set of incomes
	 */
	public Incomes( String name, String earner, Simulation sim) {
		super(name, earner, null, null, 0, sim);
		sources = new Income[MAX_SOURCES];
		numSources = 0;
		max_calculated = sim.firstYear - 1;
	}

	/**
	 * add a new expense to a collection of expenses
	 * 
	 * @param source			income source to add to collection			
	 * 
	 * @throws NoSuchElementException
	 */
	public void addSource( Income source ) 
	throws NoSuchElementException {
		if (numSources >= MAX_SOURCES)
			throw new NoSuchElementException("Too many income sources");

		sources[numSources] = source;
		numSources++;
	}
	
	/**
	 * return taxable income (from all sources) for specified year
	 * 
	 * @param year	
	 * 
	 * @return	sum of all taxable incomes for that year
	 */
	public int getTaxable( int year ) {
		update( year );
		return super.getTaxable(year);
	}
	
	/**
	 * return SSI income (from all sources) for specified year
	 * 
	 * @param year	
	 * 
	 * @return	sum of all SSI incomes for that year
	 */
	public int getSSI( int year ) {
		update( year );
		return super.getSSI(year);
	}
	
	/**
	 * return IRA/401K contrbutions (from all sources) for specified year
	 * 
	 * @param year	
	 * 
	 * @return	sum of all retirement contributions for that year
	 */
	public int getContribution( int year ) {
		update( year );
		return super.getContribution(year);
	}
	
	/**
	 * Ensure that the income is updated 
	 * 
	 * @param year	year for which values are required
	 */
	private void update(int year) {
		
		while( max_calculated < year ) {
			int taxable = 0;
			int contrib = 0;
			int ssi = 0;
		
			// run through all the expenses for the specified year
			for( int i = 0; i < numSources; i++ ) {
				taxable += sources[i].getTaxable(max_calculated+1);
				ssi += sources[i].getSSI(max_calculated+1);
				contrib += sources[i].getContribution(max_calculated+1);
			}
			super.setIncome( max_calculated+1, taxable, ssi, contrib );
			max_calculated++;
		}
	}
}
