package simulation;

// FIX generalize expenses to be cash-flow-streams 
//		with all the attributes of income as well as expenses

/**
 * a distinct expense, with its own value, characteristics, and growth
 * rate/shaping functions.
 * 
 * @author markk
 */
public class Expense {
	
	public String name;			// name of this expense
	
	private Envelope shape;		// expense shaping envelope
	private Rate bRate;			// growth rate for budget
	private Rate aRate;			// growth rate for actual expenses
	private Simulation sim;		// global simulation parameters
	private String subClass;	// general expense category
	
	private int max_computed;	// last year for which values are computed
	private int actuals[];		// computed or assigned values
	private int budgets[];		// computed or assigned values
	
	public boolean debug;
	
	/**
	 * Create a new expense object
	 * 
	 * @param expenseName	name of this expense
	 * @param subclass	expense sub-class (e.g. discretionary/non-discretionary)
	 * @param shapeFunc	shaping function for this expense.
	 * 					e.g. expenses that happen only for a few years
	 * 						 expenses that are load-sensitive
	 * @param rateFunc	rate function for budgeted expense
	 * @param actFunc	rate function for actual expense
	 * 					if this is null, actual = budget
	 * @param sim		global simulation parameters
	 */
	public Expense( String expenseName, 
					String subclass, Envelope shapeFunc, Rate rateFunc,
					Rate actFunc, Simulation simParms ) {
		name = expenseName;
		subClass = subclass;
		shape = shapeFunc;
		bRate = rateFunc;
		aRate = actFunc;
		sim=simParms;
		max_computed = sim.firstYear;
		debug = false;
		actuals = new int[sim.numYears];
		budgets = new int[sim.numYears];
		
		// all expenses start out zero
		for( int i = 0; i < sim.numYears; i++ ) {
			actuals[i] = 0;
			budgets[i] = 0;
		}
	}
	
	/**
	 * set the actual expense amount for a specified year
	 * 
	 * @param year	year for which expense is being set (typically starting year)
	 * @param actual	amount of expense for that year
	 * @param budgeted amount for that year
	 */
	public void setExpense( int year, int actual, int budgeted ) {
		int thisX = sim.getYearX(year);
		
		actuals[thisX] = actual;
		budgets[thisX] = budgeted;
		
		if (max_computed < year)
			max_computed = year;
	}
	
	public void setExpense( int year, int amount ) {
		setExpense( year, amount, amount );
	}
	
	/**
	 * return the actual amount of an expense for a specified year
	 *
	 * @param year	Year for which expense is to be returned
	 * 
	 * @return	amount of expense for that year
	 */
	public int getExpense( int year ) {
		int thisX = sim.getYearX(year);

		compute(year);
		return actuals[thisX];
	}

	/**
	 * return the budgeted amount of an expense for a specified year
	 *
	 * @param year	Year for which expense is to be returned
	 * 
	 * @return	expense budget for that year
	 */
	public int getBudget( int year ) {
		int thisX = sim.getYearX(year);

		compute(year);
		return budgets[thisX];
	}
	
	/**
	 * string form of expense for a specified year
	 * 
	 * @param year	desired year
	 * @return		XML representation of expense state
	 */
	public String toString( int year ) {
		sim.getYearX(year);
		if (year > max_computed)
			compute( year );
		
		// if this expense doesn't exist, return null
		if (shape != null && shape.scaleForYear(year) == 0)
			return null;
		
		/*
		 * NOTE: I use get routines rather than directly accessing
		 *  	 the variables because the get routines may be 
		 *  	 over-loaded by sub-classes ... which might still
		 *  	 want to use this method.
		 */
		String result = "<expense ";
			result += String.format("name=\"%s\" ", name);
			result += String.format("subclass=\"%s\" ", subClass);
			result += String.format("year=\"%s\" ", year);
			result += String.format("actual=\"$%d\" ", getExpense(year));
			result += String.format("budget=\"$%d\" ", getBudget(year));
		result += ">";
		return result;
	}
	public String toString() {
		return toString( max_computed );
	}
	

	/**
	 * apply growth functions to compute cash flow for given year
	 * <P>
	 * 
	 * @param year	Year to be brought up to date
	 */
	public void compute(int year) {
		sim.getYearX(year);
		
		// if we don't (yet) have a value for the specified year,
		//	  use the rate and shaping functions to compute values
		//	  starting with the last year already computed
		while( year > max_computed ) {
			int thisX = max_computed - sim.firstYear;
			double env = (shape == null) ? 1.0 :
				shape.scaleForYear(max_computed + 1);
			double bGrowth = (bRate == null) ? 0.0 : 
							bRate.rateForYear(max_computed + 1);
			double bNew = (1+bGrowth) * env * budgets[thisX];
			budgets[thisX+1] = (int) bNew;
			
			double aGrowth = (aRate == null) ? bGrowth : 
							aRate.rateForYear(max_computed + 1);
			double aNew = (1+aGrowth) * env * actuals[thisX];
			actuals[thisX+1] = (int) aNew;
			
			max_computed++;
		}
	}
}
