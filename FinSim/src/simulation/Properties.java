package simulation;

import java.util.NoSuchElementException;

/**
 * a collection of properties.
 * 
 * because these are simply containers for groups of properties,
 * we expose the array of properties
 * 
 * @author Mark
 */
public class Properties extends Property {
	// perhaps I should make this dynamic some day
	private static final int MAX_PROPERTIES = 50;
	
	public Property property[];
	public int numProperties;
	private int max_computed;
	
	private int tax[];		// aggregate tax per year
	private int ins[];		// aggregate property insurance per year
	private int improve[];	// aggregate improvements
	private Simulation sim;	// global simulation parameters
	
	/**
	 * allocate a set of properties
	 * @param subclass type of property
	 */
	public Properties( String name, String subclass, Simulation simParms ) {
		
		super( name, subclass, null, null, null, null, simParms );
		sim = simParms;
		property = new Property[MAX_PROPERTIES];
		numProperties = 0;
		max_computed = sim.firstYear - 1;

		
		tax = new int[sim.numYears];
		ins = new int[sim.numYears];
		improve = new int[sim.numYears];
		for( int i = 0; i < sim.numYears; i++ ) {
			tax[i] = 0;
			ins[i] = 0;
			improve[i] = 0;
		}
	}
	
	/**
	 * add a new expense to a collection of expenses
	 * 
	 * @param property			property to add to collection			
	 * 
	 * @throws NoSuchElementException if too many properties
	 */
	public void addProperty( Property prop ) 
						throws NoSuchElementException {
		if (numProperties >= MAX_PROPERTIES)
			throw new NoSuchElementException("Too many properties");
		
		property[numProperties] = prop;
		numProperties++;
	}

	/**
	 * update the composite pseudo-property for the specified year
	 * 
	 * @param year
	 */
	private void update( int year ) {
		//usually, it is already up to date
		if (max_computed >= year)
			return;
		
		int value = 0;
		int basis = 0;
		int assess = 0;
		int improvements = 0;
		int taxes = 0;
		int insurance = 0;
		
		for( int i = 0; i < numProperties; i++ ) {
			value += property[i].getValue(year);
			basis += property[i].getBasis(year);
			assess += property[i].getAssessed(year);
			improvements += property[i].getImprovements(year);
			taxes += property[i].getTax(year);
			insurance += property[i].getInsurance(year);
		}
		
		// push all of these values to the aggregation asset
		super.setValue(year, value, assess, basis );
		tax[year-sim.firstYear] = taxes;
		ins[year-sim.firstYear] = insurance;
		improve[year-sim.firstYear] = improvements; 
		
		max_computed = year;
	}
	
	/**
	 * return the total value of improvements made during a year
	 * 
	 * @param y		year for which value is requested
	 * @return		total property improvements for that year
	 */
	public int getImprovements(int y) {
		int thisX = sim.getYearX(y);
		update(y);
		return improve[thisX];
	}
	
	/**
	 * return the total value of all properties in the set
	 * 
	 * @param y		year for which value is requested
	 * @return		total property value for that year
	 */
	public int getValue(int y) {
		update(y);
		return super.getValue(y);
	}

	/**
	 * return the total property taxes on all properties in the set
	 * 
	 * @param y		year for which tax is requested
	 * @return		total property tax for that year
	 */
	public int getTax( int year ) {
		int thisX = sim.getYearX(year);
		update(year);
		return tax[thisX];
	}

	/**
	 * return the total insurance on all properties in the set
	 * 
	 * @param y		year for which insurance is requested
	 * @return		total property insurance for that year
	 */
	public int getInsurance( int year ) {
		int thisX = sim.getYearX(year);
		update(year);
		return ins[thisX];
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