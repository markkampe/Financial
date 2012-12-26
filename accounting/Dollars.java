package accounting;

// CONSIDER Dollars extends Number

/**
 * input/output methods for converting between ints
 * (in cents) and character string dollar amounts
 * 
 * @author markk
 */
public class Dollars {
	
	// this is the output-width for all dollar amounts
	public static final int width = 12;	// "($######.##)"
	
	
	/**
	 * @param String to be parsed
	 */
	public static int Parse( String str ) throws NumberFormatException {
		// we start with our original length
		int start = 0;
		int end = str.length();
		int sign = 1;
		
		// make sure we aren't parsing an empty string
		if (end < 1)
			throw new NumberFormatException("Empty Amount");
		
		// see if the number is negative
		char c = str.charAt(start);
		if (c == '(') {
			sign = -1;
			end--;		// expect a closing paren at the end
			c = str.charAt(++start);
		} else if (c == '-') {
			sign = -1;
			c = str.charAt(++start);
		}

		// first/next character may be a dollar sign
		if (c == '$')
			start++;
		
		int amount;
		
		// see if there is a decimal point;
		int decimal = str.indexOf('.', start);
		if (decimal < 0) {
			// integer number of dollars
			try {
				amount = Integer.parseInt(str.substring(start,end)) * 100;
			} catch (NumberFormatException e) {
				throw new NumberFormatException( "invalid dollar amount " + e.getMessage());
			}
		} else {
			// dollars and cents
			try {
				amount = Integer.parseInt(str.substring(start,decimal)) * 100;
			} catch (NumberFormatException e ) {
				throw new NumberFormatException( "invalid dollar amount " + e.getMessage());
			}
			try {
				amount += Integer.parseInt(str.substring(decimal+1,end));
			} catch (NumberFormatException e) {
				throw new NumberFormatException( "invalid cents amount " + e.getMessage());
			}

		}	
		
		amount *= sign;
		return amount;
	}
	
	
	/**
	 * format an amount as a fixed width dollars & cents
	 * with parentheses for negative numbers.
	 * 
	 * Note: they are fixed width so the decimals line up
	 */
	public static String toString( int amount ) {
		final String negFormat = "($%d.%02d)";
		final String posFormat = " $%d.%02d ";
		String s = (amount < 0) ?
					String.format(negFormat, -amount/100, -amount%100) :
					String.format(posFormat, amount/100, amount%100);
		
		// left-pad it to the target column width
		return String.format("%" + width + "s", s );	
	}
}
