package simulation;

import java.util.NoSuchElementException;

/**
 * a collection of expenses.
 * 
 * because these are simply containers for groups of expenses,
 * we expose the array of expenses
 * 
 * @author Mark
 */
public class Expenses extends Expense {
	// perhaps I should make this dynamic some day
	private static final int MAX_EXPENSES = 50;
	
	public Expense expenses[];
	public int numExpenses;
	
	private int max_calculated;
	
	/**
	 * allocate a set of expenses
	 */
	public Expenses( String name, String subclass, Simulation sim ) {
		
		super(name, subclass, null, null, null, sim);
		
		expenses = new Expense[MAX_EXPENSES];
		numExpenses = 0;
		max_calculated = sim.firstYear - 1;
	}
	
	/**
	 * add a new expense to a collection of expenses
	 * 
	 * @param expense			expense to add to collection			
	 * @param isDiscretionary	is this expense discretionary
	 * 
	 * @throws NoSuchElementException
	 */
	public void addExpense( Expense expense, boolean isDiscretionary ) 
						throws NoSuchElementException {
		if (numExpenses >= MAX_EXPENSES)
			throw new NoSuchElementException("Too many expenses");
		
		expenses[numExpenses] = expense;
		numExpenses++;
	}
	
	/**
	 * return the sum of all the expenses for a specified year
	 * 
	 * @param year	year for which expenses are desired
	 * 
	 * @return	total (requested) expenses for specified year
	 */
	public int getExpense( int year ) {
		update(year);
		return super.getExpense(year);
	}
	
	/**
	 * return the sum of all the budgets for a specified year
	 * 
	 * @param year	year for which expenses are desired
	 * 
	 * @return	total (requested) budgets for specified year
	 */
	public int getBudget( int year ) {
		update(year);
		return super.getBudget(year);
	}

	/**
	 * Ensure that the pseudo_expense is updated 
	 * 
	 * @param year	year for which values are required
	 */
	private void update(int year) {
		
		while( max_calculated < year ) {
			int act = 0;
			int bgt = 0;
		
			// run through all the expenses for the specified year
			for( int i = 0; i < numExpenses; i++ ) {
				act += expenses[i].getExpense(max_calculated+1);
				bgt += expenses[i].getBudget(max_calculated+1);
			}
			super.setExpense( max_calculated+1, act, bgt );
			max_calculated++;
		}
	}
}