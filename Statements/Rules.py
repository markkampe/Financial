#!/usr/bin/python
#
#   This class implements the digesting and execution of rules for
#   mapping ledger descriptions into accounts and comments
#


class Rule:
    """
        a rule is:
            a wild-card pattern (not an RE)
            an account name to use (if pattern matches)
            a description to use (if pattern matches)
            how to process the results
                aggregate ... into a category subtotal
                replace ... keep it separate with a new description
                preserve ... keep it separate with original description
                combine ... keep it separate combining new and original
    """
    def __init__(self, pattern, account, descr, process):
        self.pat = pattern
        self.acct = account
        self.descr = descr
        self.process = process

import fnmatch  # we use shell wild cards rather than true REs


class Rules:
    """
    """
    def __init__(self, filename):
        """
            constructor for a new ruleset
        """
        # FIX ... read these in from the specified rules file
        self.rules = []
        self.rules.append(Rule("SAN*BER*TAX*", "Basic", "SBDO Prop Taxes", "replace"))
        self.rules.append(Rule("LA Co TTC Paymnt*", "Basic", "LA Prop Taxes", "replace"))
        self.rules.append(Rule("Online Payment * To State Farm*", "Basic", "home insurance", "replace"))

        self.rules.append(Rule("THE GAS COMPANY*", "Utilities", "gas", "replace"))
        self.rules.append(Rule("LADWP*", "Utilities", "DWP", "replace"))
        self.rules.append(Rule("ATT*", "Utilities", "phone", "replace"))
        self.rules.append(Rule("TIME WARNER*", "Utilities", "cable", "replace"))

        self.rules.append(Rule("*ORCHARD SUPPLY*", "Household", "OSH", "aggregate"))
        self.rules.append(Rule("*HOME DEPOT*", "Household", "home depot", "aggregate"))
        self.rules.append(Rule("LOWES *", "Household", "Lowes", "aggregate"))
        self.rules.append(Rule("ARMSTRONG*", "Household", "nursery", "aggregate"))
        self.rules.append(Rule("WWW.RSABG.ORG*", "Household", "nursery", "aggregate"))
        self.rules.append(Rule("J&P*PARKSEED*", "Household", "nursery", "aggregate"))

        self.rules.append(Rule("SHELL OIL*", "Transportation", "gas", "aggregate"))
        self.rules.append(Rule("CHEVRON CC*", "Transportation", "gas", "aggregate"))
        self.rules.append(Rule("COSTCO GAS*", "Transportation", "gas", "aggregate"))
        self.rules.append(Rule("USA *", "Transportation", "gas", "aggregate"))
        self.rules.append(Rule("76 *", "Transportation", "gas", "aggregate"))
        self.rules.append(Rule("ARCO PAYPOINT**", "Transportation", "gas", "aggregate"))
        self.rules.append(Rule("*GEICO*", "Transportation", "m/c insurance", "replace"))
        self.rules.append(Rule("ST OF CA DMV*", "Transportation", "registration", "combine"))
        self.rules.append(Rule("MERCURY CASUALTY*", "Transportation", "car insurance", "replace"))
        self.rules.append(Rule("Online Payment * To Auto Club*", "Transportation", "AAA membership", "replace"))
        self.rules.append(Rule("Online Payment * To Mercury Insurance*", "Transportation", "car insurance", "replace"))
        self.rules.append(Rule("LAX AIRPORT LOT*", "Transportation", "parking", "aggregate"))
        self.rules.append(Rule("BOB HOPE AIRPORT*", "Transportation", "parking", "aggregate"))
        self.rules.append(Rule("AMPCO PARKING*", "Transportation", "parking", "aggregate"))
        self.rules.append(Rule("ABM PARKING*", "Transportation", "parking", "aggregate"))

        self.rules.append(Rule("UNIONSTATIONFLYAWAY*", "Vacation", "shuttle", "aggregate"))

        self.rules.append(Rule("BELLA VISTA INN*", "Commuting", "lodging", "aggregate"))
        self.rules.append(Rule("SOUTHWES*", "Commuting", "air fare", "combine"))

        self.rules.append(Rule("AMC MERCADO*", "Food-and-Fun", "movies", "aggregate"))
        self.rules.append(Rule("PACIFIC THEATRES*", "Food-and-Fun", "movies", "aggregate"))

        self.rules.append(Rule("TONYS ON THE PIER*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("REAL FOOD DAILY*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("MIMIS CAFE*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("ISLANDS REST*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("MORRISON*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("VIVA MADRID*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("EL ARCO IRIS REST*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("THE BRIT*", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("ELEPHANT BAR *", "Food-and-Fun", "dinner", "aggregate"))
        self.rules.append(Rule("OOMASA INC*", "Food-and-Fun", "dinner", "aggregate"))

        self.rules.append(Rule("PEDRO'S RESTAURANT*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("TOMATINA*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("SUBWAY *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("CHILI'S*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("LAKESIDE CAFE*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("ATHENA GRILL*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("MCDONALD'S*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("TACO BELL*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("CARLS JR*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("DENNY'S INC*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("SPECIALTY*S CAFE*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("SWEET TOMATOES *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("PSYCHO DONUTS*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("THE CHEESE STEAK SHOP*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("TASTY SUBS *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("ST JOHNS BAR & GRILL*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("SMOKING PIG*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("AY CARAMBA*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("RED ROBIN *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("QDOBA *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("IN-N-OUT BURGER *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("RUBY*S DINETTE*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("YAN CAN *", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("THE GREYHOUND*", "Food-and-Fun", "lunch", "aggregate"))
        self.rules.append(Rule("Zankou Chicken*", "Food-and-Fun", "lunch", "aggregate"))

        self.rules.append(Rule("*SUPERIOR*GROCER*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("FOOD4LESS*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("LUCKY *", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("VONS *", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("RALPHS *", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("SUPER KING MARKET *", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("WHOLEFDS*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("SMARTNFINAL*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("TRADER JOE'S*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("COSTCO WHSE*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("FRESH & EASY*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("SPROUTS FARMERS MAR*", "Groceries", "groceries", "aggregate"))
        self.rules.append(Rule("PETCO*", "Groceries", "dog food", "aggregate"))
        self.rules.append(Rule("BEVERAGES & MORE*", "Groceries", "alcohol", "aggregate"))

        self.rules.append(Rule("Online Payment * To Genworth Life*", "MD", "LTC insurance", "replace"))
        self.rules.append(Rule("CONEXIS*", "MD", "FSA reimb", "replace"))

        self.rules.append(Rule("NCSU STUDENT HEALTH", "MD", "CK ov", "replace"))
        self.rules.append(Rule("SQ *ASPIRE COUNSELING GRO*", "MD", "CK ov", "replace"))
        self.rules.append(Rule("JOHN LAWRENCE GARWOOD *", "MD", "MK OD", "replace"))
        self.rules.append(Rule("KP RX*", "MD", "Prescriptions", "combine"))

        self.rules.append(Rule("BLUE SHIELD OF CA*", "MD", "JK ins", "replace"))
        self.rules.append(Rule("FSI*HCSC PREMIUM PMT*", "MD", "JK ins", "replace"))
        self.rules.append(Rule("USC CARE MEDICAL GROUP*", "MD", "JK ov USC", "replace"))
        self.rules.append(Rule("HUNTINGTON DERMATOLOGY*", "MD", "JK ov Huntington", "replace"))
        self.rules.append(Rule("*JACKLIN POLADIAN MD*", "MD", "JK ov Poladian", "replace"))
        self.rules.append(Rule("*ELEANOR LEUNG MD*", "MD", "JK ov Leung", "replace"))
        self.rules.append(Rule("LENS.COM*", "MD", "JK contacts", "replace"))

        self.rules.append(Rule("ANIMAL SPECIALTY GROUP*", "MD", "vet (animal specialty)", "replace"))
        self.rules.append(Rule("LA VILLAGE VET*", "MD", "vet (village)", "replace"))

        self.rules.append(Rule("SPORT CHALET* DIRECT DEP*", "Hobby", "MK SCUBA pay", "replace"))
        self.rules.append(Rule("Onine Payment * To Divers Alert Network*", "Hobby", "DAN mshp/ins", "replace"))
        self.rules.append(Rule("VICENCIA AND BUCKLEY*", "Hobby", "liability ins", "replace"))

        self.rules.append(Rule("SUPERCUTS*", "Clothing", "MK h/c", "replace"))

        self.rules.append(Rule("ACM", "Misc", "MK ACM dues", "replace"))
        self.rules.append(Rule("INTL SOC ARBORICULTURE", "Misc", "LK ISA dues", "replace"))
        self.rules.append(Rule("NATURAL HISTORY MUSEUM*", "Misc", "Nat Hist mship", "replace"))
        self.rules.append(Rule("HUNTINGTON *", "Misc", "Huntington mship", "replace"))
        self.rules.append(Rule("USPS*", "Misc", "postage", "replace"))

        self.rules.append(Rule("HARBOR FREIGHT TOOLS*", "Toys", "Harbor Freight", "replace"))
        self.rules.append(Rule("THINKGEEK*", "Toys", "ThinkGeek", "replace"))
        self.rules.append(Rule("SPARKFUN ELECTRONICS*", "Toys", "SparkFun", "replace"))

        self.rules.append(Rule("AQUA LUNG*", "Hobby", None, "preserve"))

        self.rules.append(Rule("WITHDRAW*", "Cash", "withdrawal", "aggregate"))
        self.rules.append(Rule("ATM WITHDRAWAL*", "Cash", "ATM", "aggregate"))
        self.rules.append(Rule("NON-CHASE ATM WITHDRAW*", "Cash", "ATM", "aggregate"))
        self.rules.append(Rule("NON-CHASE ATM FEE-WITH*", "Cash", "ATM fee", "aggregate"))
        self.rules.append(Rule("THEODORE PAYNE F PAYROLL*", "Deposit", "LK pay", "aggregate"))
        self.rules.append(Rule("FUTUREWEI TECHNO PAYROLL*", "Deposit", "MK pay", "aggregate"))
        self.rules.append(Rule("FUTUREWEI TECHNO PAYMENT*", "Deposit", "expense reimb", "aggregate"))
        self.rules.append(Rule("HUAWEI TECH. INV PAYMENT*", "Deposit", "purchase reim", "aggregate"))
        self.rules.append(Rule("AMERICAN EXPRESS ACH PMT*", "CreditCard", "AMEX autopay", "aggregate"))
        self.rules.append(Rule("*PPD ID: CITICARDAP*", "CreditCard", "CitiCard autopay", "aggregate"))
        self.rules.append(Rule("AUTOMATIC PAYMENT - THANK*", "CreditCard", "autopay", "aggregate"))
        self.rules.append(Rule("AUTOPAY PAYMENT - THANK YOU*", "CreditCard", "autopay", "aggregate"))
        self.rules.append(Rule("CHASE*AUTOPAY *", "CreditCard", "Chase autopay", "aggregate"))
        self.rules.append(Rule("FID BKG SVC LLC*", "Transfer", "(FIDO)", "aggregate"))
        self.rules.append(Rule("LENDING CLUB*", "Transfer", "(Lending Club)", "aggregate"))
        self.rules.append(Rule("BANK OF AMERICA*FndTrnsfr*", "Transfer", "(BofA)", "aggregate"))

        self.rules.append(Rule("IRS*USATAXPYMT*", "Taxes", "IRS", "replace"))
        self.rules.append(Rule("FRANCHISE TAX BO PAYMENTS*", "Taxes", "CA", "replace"))

        # catch-all heuristics that probably work, but should be checked
        self.rules.append(Rule("* GAS STATION *", "Transportation", "gas", "combine"))
        self.rules.append(Rule("* GAS STATION", "Transportation", "gas", "combine"))

        self.rules.append(Rule("* SUPERMARKET *", "Groceries", None, "preserve"))
        self.rules.append(Rule("* SUPERMARKET", "Groceries", None, "preserve"))
        self.rules.append(Rule("* MARKET *", "Groceries", None, "preserve"))
        self.rules.append(Rule("* MARKET", "Groceries", None, "preserve"))
        self.rules.append(Rule("* MARKETS", "Groceries", None, "preserve"))
        self.rules.append(Rule("* GROCERY *", "Groceries", None, "preserve"))

        self.rules.append(Rule("* RESTAURANT *", "Food-and-Fun", "dinner", "combine"))
        self.rules.append(Rule("* RESTAURANT", "Food-and-Fun", "dinner", "combine"))
        self.rules.append(Rule("* RISTORANTE", "Food-and-Fun", "dinner", "combine"))
        self.rules.append(Rule("* BAR *", "Food-and-Fun", "dinner", "combine"))
        self.rules.append(Rule("* BAR", "Food-and-Fun", "dinner", "combine"))
        self.rules.append(Rule("* GRILL *", "Food-and-Fun", "dinner", "combine"))
        self.rules.append(Rule("* GRILL", "Food-and-Fun", "dinner", "combine"))

        self.rules.append(Rule("THEODORE PAYNE FOUNDAT*", "Household", "nursery", "replace"))

        # medical, but not sure what
        self.rules.append(Rule("KAISER *", "MD", None, "preserve"))
        self.rules.append(Rule("Online Payment * To Kaiser *", "MD", None, "preserve"))
        self.rules.append(Rule("QDI*QUEST DIAGNOSTICS*", "MD", None, "preserve"))
        self.rules.append(Rule("CVS/PHARMACY*", "MD", None, "preserve"))
        self.rules.append(Rule("RITE AID *", "MD", None, "preserve"))
        self.rules.append(Rule("WALGREENS *", "MD", None, "preserve"))

        # guesses based on what we usually buy in these stores
        self.rules.append(Rule("SPORT CHALE*", "Hobby", None, "preserve"))
        self.rules.append(Rule("BIG 5 SPORTING GOODS*", "Clothing", None, "preserve"))
        self.rules.append(Rule("REI *", "Clothing", None, "preserve"))
        self.rules.append(Rule("TARGET.COM*", "Clothing", None, "preserve"))
        self.rules.append(Rule("TARGET *", "Clothing", None, "preserve"))
        self.rules.append(Rule("SUR LA TABLE *", "Household", None, "preserve"))
        self.rules.append(Rule("POTTERY BARN*", "Household", None, "preserve"))

        self.rules.append(Rule("DELTA AIR*", "Vacations", None, "preserve"))

    def match(self, desc):
        """
            try to find a rule for this description

            Parameters:
                description (unquoted string)

            Returns:
                account name (or None)
                (boolean) should this line be aggregated
                quoted description string
        """
        # look for a matching rule
        for r in self.rules:
            if fnmatch.fnmatch(desc, r.pat):
                p = r.process
                if p == "aggregate":
                    return (r.acct, True, '"' + r.descr + '"')
                elif p == "replace":
                    return (r.acct, False, '"' + r.descr + '"')
                elif p == "combine":
                    newdesc = '"' + r.descr + ': ' + desc + '"'
                    return (r.acct, False, newdesc)
                else:   # preserve
                    return (r.acct, False, '"' + desc + '"')

        return (None, False, '"' + desc + '"')
