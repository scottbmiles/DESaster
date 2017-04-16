# DESaster Modules

`entities.py` **Module of classes for implementing DESaster entities, such as households and businesses.**

Classes:
`Entity(object)`
`Owner(Entity)`
`Household(Entity)`
`OwnerHousehold(Owner, Household)`
`RenterHousehold(Entity, Household)`
`Landlord(Owner)`

`structures.py` **Module of classes that represent different types of buildings used by DESaster entities.**

Classes:
`Building`
`SingleFamilyResidential(Building)`

`financial.py` **Module of classes for implementing DESaster financial recovery programs.**

Classes:
`FinancialRecoveryProgram`
`HomeLoan(FinancialRecoveryProgram)`
`OwnersInsurance(FinancialRecoveryProgram)`
`IndividualAssistance(FinancialRecoveryProgram)` 

`technical.py` **Module of classes for implementing DESaster technical recovery programs.**

Classes:
`InspectionProgram`
`PermitProgram(InspectionProgram)`
`EngineeringAssessment(InspectionProgram)`
`RepairProgram(InspectionProgram)`
`RepairStockProgram(InspectionProgram)`

`policies.py` **Module of classes that implement compound policies for custom arrangements of DESaster recovery programs.**

Classes:
`RecoveryPolicy`
`Insurance_IA_Loan_Sequential(RecoveryPolicy)`

`io.py` **Module of classes and functions for input/output related to DESaster.**

Classes:
`DurationProbabilityDistribution`

Functions
`random_duration_function`
`importSingleFamilyResidenceStock` 

`config.py` **Module for defining variables for a suite of DESaster parameters. **


