package simulation;

/**
 * simulated income stream with its own distinct rate, shape
 * and tax consequences
 * 
 * @author markk
 */
public class Income {
	private String name;		// name of this income source
	private String earnedBy;	// who earned it
	
	private Envelope shapingFunction;
	private Rate rateFunction;
	private int iraContrib;		// annual IRA/401K contributions
	
	private Simulation sim;		// global simulation parameters
	private int max_computed;	// last year for which values are computed
	
	private int taxable[];		// total taxable income
	private int retirement[];	// non-taxed retirement contributions
	private int ssi_income[];	// eligible for SSI withholding
	
	public boolean debug;		// are we debugging this income source
	
	/**
	 * Create a new income stream object
	 * 
	 * @param source	name of this income source
	 * @param earner 	name of person who earned it
	 * @param shapeFunc	shaping function for this expense
	 * @param rateFunc	rate function for this expense
	 * @param contrib	annual retirement contribution
	 * @param sim.firstYear	first year of simulation
	 * @param sim.numYears	number of years to be simulated
	 */
	public Income( String source, String earner, 
					Envelope shapeFunc, Rate rateFunc,
					int contribution, Simulation simParms ) {
		name = source;
		earnedBy = earner;
		shapingFunction = shapeFunc;
		rateFunction = rateFunc;
		iraContrib = contribution;
		sim = simParms;
		max_computed = sim.firstYear;
		taxable = new int[sim.numYears];
		retirement = new int[sim.numYears];
		ssi_income = new int[sim.numYears];
		debug = false;
		
		// all expenses start out zero
		for( int i = 0; i < sim.numYears; i++ ) {
			taxable[i] = 0;
			retirement[i] = 0;
			ssi_income[i] = 0;
		}
	}
	
	/**
	 * set the gross income for a specified year
	 * 
	 * @param year	year for which expense is being set (typically starting year)
	 * @param income	amount of taxable income for that year
	 * @param ssi		amount of SSI eligible income for that year
	 * @param contrib	non-taxable retirement contributions
	 */
	public void setIncome( int year, int income, int ssi, int contrib ) {
		sim.getYearX(year);
		
		taxable[year - sim.firstYear] = income;
		retirement[year - sim.firstYear] = contrib;
		ssi_income[year - sim.firstYear] = ssi;
		if (max_computed < year)
			max_computed = year;
	}
	
	public void setIncome( int year, int income ) {
		setIncome( year, income, income, iraContrib );
	}
	
	public void setIncome( int year, int income, int contrib ) {
		setIncome( year, income, income, contrib );
	}
	
	/**
	 * return the taxable income amount for a specified year
	 *
	 * NOTE: incomes are not computed until they are asked for
	 *
	 * @param year	Year for which income is to be returned
	 * 
	 * @return	amount of taxable income for that year
	 */
	public int getTaxable( int year ) {
		int thisX = sim.getYearX(year);

		compute(year);
		return taxable[thisX];
	}
	
	/**
	 * return the SSI income amount for a specified year
	 *
	 * NOTE: incomes are not computed until they are asked for
	 *
	 * @param year	Year for which income is to be returned
	 * 
	 * @return	amount of SSI income for that year
	 */
	public int getSSI( int year ) {
		int thisX = sim.getYearX(year);

		compute(year);
		return ssi_income[thisX];
	}

	/**
	 * return the IRA/401K contribution for a specified year
	 *
	 * NOTE: incomes are not computed until they are asked for
	 *
	 * @param year	Year for which contribution is to be returned
	 * 
	 * @return	amount of contribution for that year
	 */
	public int getContribution( int year ) {
		int thisX = sim.getYearX(year);

		compute(year);
		return retirement[thisX];
	}

	public String toString( int year ) {
		sim.getYearX(year);
		
		// if income source does not exist this year, return null
		if (shapingFunction != null && shapingFunction.scaleForYear(year) == 0)
			return null;
		
		if (year > max_computed)
			compute( year );
		
		/*
		 * NOTE: I use get routines rather than directly accessing
		 *  	 the variables because the get routines may be 
		 *  	 over-loaded by sub-classes ... which might still
		 *  	 want to use this method.
		 */
		String result = "<income ";
			result += String.format("name=\"%s\" ", name);
			result += String.format("earner=\"%s\" ", earnedBy);
			result += String.format("year=\"%s\" ", year);
			result += String.format("taxable=\"$%d\" ", getTaxable(year));
			result += String.format("ira=\"$%d\" ", getContribution(year));
			result += String.format("ssi_income=\"$%d\" ", getSSI(year));
		result += ">";
		return result;
	}
	
	public String toString() {
		return toString( max_computed );
	}
	
	/**
	 * If we do not yet have values for a desired year, use
	 * the rate and shaping functions (and the values already
	 * computed) to compute (up to) the requested year.
	 * 
	 * @param year	for which values are required
	 */
	public void compute(int year) {
		
		sim.getYearX(year);
		
		while( year > max_computed ) {
			double rate = (rateFunction == null) ? 0.0 : 
				rateFunction.rateForYear(max_computed + 1);
			double shape = (shapingFunction == null) ? 1.0 :
				shapingFunction.scaleForYear(max_computed + 1);
			int lastX = max_computed - sim.firstYear;
			double newvalue = (1+rate) * taxable[lastX] * shape;
			taxable[lastX + 1] = (int) newvalue;
			if (iraContrib > 0)
				retirement[lastX + 1] = (int) (iraContrib * shape);
			if (ssi_income[lastX] == taxable[lastX])
				ssi_income[lastX+1] = (int) (taxable[lastX+1] * shape);
			
			max_computed++;
		}
	}
}
