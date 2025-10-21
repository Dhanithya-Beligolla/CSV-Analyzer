import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

# ------------------ MAPPINGS (GUID/ID -> READABLE TEXT) ------------------
DEPT_MAP = {
    "bde378e8-7161-f011-bec1-6045bd1dc2bf": "Account maintenance",
    "c59389b8-1e32-f011-8c4e-6045bd1e9a24": "ATM CRM PAY AND GO IPAL",
    "37dfc39b-1e32-f011-8c4e-6045bd1e9a24": "ATM located branch",
    "f75c2eff-2636-f011-8c4d-6045bd1e9a24": "Bank Guarantee",
    "8d0a4afa-1d32-f011-8c4e-6045bd1e9a24": "Branch",
    "105fb540-7261-f011-bec1-6045bd1dc2bf": "Branch Banking Support",
    "3aba8e66-1e32-f011-8c4e-6045bd1e9a24": "Businees System",
    "e6782336-1e32-f011-8c4e-6045bd1e9a24": "Call centre",
    "6640e2e9-6931-f011-8c4e-6045bd1e9a24": "Card center dispute",
    "0c1dfc20-7261-f011-bec1-6045bd1dc2bf": "Card center letters",
    "96c214d4-6931-f011-8c4e-6045bd1e9a24": "Card center merchant promotions",
    "db5799cd-6931-f011-8c4e-6045bd1e9a24": "Card center operations dispacthing",
    "0a4c4cb3-6931-f011-8c4e-6045bd1e9a24": "Card center operations general",
    "45cb71dc-6931-f011-8c4e-6045bd1e9a24": "Card center payments",
    "52cb71dc-6931-f011-8c4e-6045bd1e9a24": "Card center risk",
    "c55db1f7-7161-f011-bec1-6045bd1dc2bf": "Card products",
    "a13d33f1-7161-f011-bec1-6045bd1dc2bf": "Card sales",
    "56274751-7261-f011-bec1-6045bd1dc2bf": "Central Reconcilation",
    "344c8736-7261-f011-bec1-6045bd1dc2bf": "Compliance department",
    "5113473c-1e32-f011-8c4e-6045bd1e9a24": "Debit Card issuing",
    "c6cdfd2f-1e32-f011-8c4e-6045bd1e9a24": "Debit card operations",
    "cb7f057e-1e32-f011-8c4e-6045bd1e9a24": "DFCC One Technical Aspects",
    "32769210-7261-f011-bec1-6045bd1dc2bf": "DPS",
    "10d1fa0b-1e32-f011-8c4e-6045bd1e9a24": "Merchant Acquiring",
    "9a2701ff-7161-f011-bec1-6045bd1dc2bf": "Merchant Operations",
    "11384d5f-1e32-f011-8c4e-6045bd1e9a24": "Online Banking Technical Aspects",
    "be4af0c1-6931-f011-8c4e-6045bd1e9a24": "PFS credit card processing",
    "b89d3fcd-f635-f011-8c4d-6045bd1e9a24": "PFS Recoveries",
    "ba4af0c1-6931-f011-8c4e-6045bd1e9a24": "PMO",
    "c6d960e9-2736-f011-8c4d-6045bd1e9a24": "Products & Clients On Boarding Branch",
    "15b18105-7261-f011-bec1-6045bd1dc2bf": "Remmitance Services",
    "14b18105-7261-f011-bec1-6045bd1dc2bf": "Remmitances",
    "012d0b2b-7261-f011-bec1-6045bd1dc2bf": "Service Delivery",
    "0d1dfc20-7261-f011-bec1-6045bd1dc2bf": "Service Experience Unit",
}

SLA_MAP = {
    "57fba769-5768-f011-bec3-6045bd21ddb0": "1",
    "aca00ba8-1f3d-f011-877b-6045bd1e9a24": "14",
    "8cfd0d9d-1f3d-f011-877b-6045bd1e9a24": "2",
    "8a79dfb1-1f3d-f011-877b-6045bd1e9a24": "21",
    "3666d92d-b866-f011-b4cc-6045bd21ddb0": "3",
    "0ffe5611-e659-f011-bec1-6045bd1dc2bf": "45",
    "8dfd0d9d-1f3d-f011-877b-6045bd1e9a24": "5",
    "8efd0d9d-1f3d-f011-877b-6045bd1e9a24": "7",
    "f5df76e3-1f3d-f011-877b-6045bd1e9a24": "90",
}

PRODUCT_MAP = {
    "bc036f06-2132-f011-8c4e-6045bd1e9a24": "Accounts",
    "68cd5f1f-2336-f011-8c4d-6045bd1e9a24": "ATM",
    "7647e74d-991e-f011-998a-6045bd1e9a24": "Credit Cards",
    "602716d9-2736-f011-8c4d-6045bd1e9a24": "CRM",
    "4fb96a55-991e-f011-998a-6045bd1e9a24": "Debit Cards",
    "bcb839e5-0936-f011-8c4d-6045bd1e9a24": "DFCC One",
    "800cd4cc-2736-f011-8c4d-6045bd1e9a24": "I Connect",
    "022a533d-991e-f011-998a-6045bd1e9a24": "Leasing",
    "b1077ab2-2036-f011-8c4d-6045bd1e9a24": "Loan",
    "329fd7e0-0836-f011-8c4d-6045bd1e9a24": "Online Banking",
    "62b032c9-a442-f011-877a-6045bd1e9a24": "Other",
    "36937767-2736-f011-8c4d-6045bd1e9a24": "Pay And Go",
    "ecdf667d-2536-f011-8c4d-6045bd1e9a24": "Trade and Remittances",
}

COMPLAINT_TITLES_MAP = {
    "f6cb0e2d-1262-f011-bec1-6045bd1dc2bf": "ATM machine not working - DFCC ATM",
    "884505ae-1162-f011-bec1-6045bd1dc2bf": "Card Stuck in ATM Machine - DFCC ATM",
    "546d6871-6d31-f011-8c4e-6045bd1e9a24": "Credit card closure letter",
    "96a014b2-1462-f011-bec1-6045bd1dc2bf": "CRM machine not working - DFCC ATM",
    "a4f183a2-f935-f011-8c4d-6045bd1e9a24": "Debit card not received",
    "4e07e22f-6d31-f011-8c4e-6045bd1e9a24": "Request to change credit card billing cycle",
    "d611f6b9-1162-f011-bec1-6045bd1dc2bf": "Transaction receipt not received - DFCC ATM",
    "5a1a3288-1162-f011-bec1-6045bd1dc2bf": "Unsuccessful ATM Withdrawal - DFCC ATM",
    "e37df076-1262-f011-bec1-6045bd1dc2bf": "Unsuccessful CRM Deposit - DFCC ATM",
    "7c7d3991-1362-f011-bec1-6045bd1dc2bf": "Unsuccessful CRM Withdrawal - DFCC ATM",
    "bf4338ff-5e35-f011-8c4d-6045bd1e9a24": "Account balance confirmation letter",
    "b8de4e72-5e35-f011-8c4d-6045bd1e9a24": "account Billing address change request",
    "b3f90e89-6a35-f011-8c4d-6045bd1e9a24": "Account Closure",
    "97230ad4-5e35-f011-8c4d-6045bd1e9a24": "Account Email address change request",
    "5d5265be-5e35-f011-8c4d-6045bd1e9a24": "Account E-statement deactivation request",
    "4d379e70-5b35-f011-8c4d-6045bd1e9a24": "Account Mobile number change",
    "17398f5a-6b35-f011-8c4d-6045bd1e9a24": "Account statements request",
    "dc308adf-0d62-f011-bec1-6045bd1dc2bf": "Account VISA confirmation letter",
    "67a539af-6e31-f011-8c4e-6045bd1e9a24": "activation /Cancellation of SMS Alerts",
    "826e45f4-6e31-f011-8c4e-6045bd1e9a24": "Activation or Cancelation of E statements",
    "6621bf2d-7761-f011-bec1-6045bd1dc2bf": "Ananthaya insuarance inquries",
    "1de30d35-2536-f011-8c4d-6045bd1e9a24": "ATM machine not working - DFCC ATM",
    "238db24e-2536-f011-8c4d-6045bd1e9a24": "ATM machine not working - DFCC Offside ATM",
    "7a1b3843-6b31-f011-8c4e-6045bd1e9a24": "Auto settlement account - SI Setup / changes",
    "4d980ed7-6c31-f011-8c4e-6045bd1e9a24": "Auto settlement account (si)- Cancellations",
    "0213b50c-2736-f011-8c4d-6045bd1e9a24": "Bank Guarantee Cancellation",
    "0113b50c-2736-f011-8c4d-6045bd1e9a24": "Bank Guarantee renewal",
    "0a495617-2736-f011-8c4d-6045bd1e9a24": "Bank Guarantee request",
    "061e54b7-5b35-f011-8c4d-6045bd1e9a24": "Bank gurantee request",
    "a8e3521f-0e62-f011-bec1-6045bd1dc2bf": "Bill payments pending",
    "f6c7168d-0e62-f011-bec1-6045bd1dc2bf": "Bill payments pending",
    "9f656b13-6d31-f011-8c4e-6045bd1e9a24": "Billing Address Change - not been done(Billing proof to be provided)",
    "5761177d-2036-f011-8c4d-6045bd1e9a24": "Cannot view accounts in DFCC One",
    "0c1e9db7-0936-f011-8c4d-6045bd1e9a24": "Cannot view accounts in Online Banking",
    "e3b2205e-0936-f011-8c4d-6045bd1e9a24": "Cannot view credit card details in Online Banking",
    "e00f0276-f935-f011-8c4d-6045bd1e9a24": "Card activation",
    "903a9a6d-0d62-f011-bec1-6045bd1dc2bf": "Card closure letters",
    "32118540-fe35-f011-8c4d-6045bd1e9a24": "Card deactivation requests",
    "a12e96be-6d31-f011-8c4e-6045bd1e9a24": "Card re-activations",
    "89f7dbad-6d31-f011-8c4e-6045bd1e9a24": "Card re-issuance",
    "fb810473-fb35-f011-8c4d-6045bd1e9a24": "Card reissunace ( Damage)",
    "a040b562-fb35-f011-8c4d-6045bd1e9a24": "Card relacement request ( Lost)",
    "1ffbc77f-6d31-f011-8c4e-6045bd1e9a24": "Card Replacement",
    "7dc6a390-6d31-f011-8c4e-6045bd1e9a24": "Card Replacement",
    "4b739f38-6e31-f011-8c4e-6045bd1e9a24": "Card replacement request – Lost Card / Expired card / product change requests",
    "2d369305-2436-f011-8c4d-6045bd1e9a24": "Card Stuck in ATM Machine - DFCC ATM",
    "2e96d46c-2436-f011-8c4d-6045bd1e9a24": "Card Stuck in ATM Machine - DFCC Offside ATM",
    "a58153c6-6d31-f011-8c4e-6045bd1e9a24": "Cash Back Account - Changes / Inquiries",
    "4a7d5290-6f31-f011-8c4e-6045bd1e9a24": "Cash back account link",
    "72f061ea-7861-f011-bec1-6045bd1dc2bf": "CEFT Chargeback Inquiries",
    "24b09d00-7961-f011-bec1-6045bd1dc2bf": "CEFT Chargeback Inquiries",
    "774f3eb9-1f32-f011-8c4e-6045bd1e9a24": "CEFT Chargeback Request",
    "6b512d2d-f835-f011-8c4d-6045bd1e9a24": "CEFT Transaction Delays",
    "3eef9611-6f31-f011-8c4e-6045bd1e9a24": "Change of Registered E-mail Address",
    "743856a3-5a35-f011-8c4d-6045bd1e9a24": "Cheques book Request",
    "102521f4-0f62-f011-bec1-6045bd1dc2bf": "Closure letters - Permanent blocked cards",
    "c717f197-fc61-f011-bec1-6045bd1dc2bf": "compliance related inquiries",
    "e53c8995-7661-f011-bec1-6045bd1dc2bf": "Credit card application status",
    "bef8e848-6d31-f011-8c4e-6045bd1e9a24": "Credit Card balance confirmation letter",
    "9ec470aa-6f31-f011-8c4e-6045bd1e9a24": "Credit card balance mismatch",
    "3e3cadf9-6c31-f011-8c4d-6045bd1e9a24": "Credit card Balance Transfer",
    "fc19389a-1062-f011-bec1-6045bd1dc2bf": "Credit card cancelation/closure request - Permanent blocked cards",
    "c5a18378-6f31-f011-8c4e-6045bd1e9a24": "Credit card cancellation",
    "6c9c533c-6d31-f011-8c4e-6045bd1e9a24": "Credit Card Cancellation Request",
    "e3ad68a0-6d31-f011-8c4e-6045bd1e9a24": "Credit card Cash back not recieved",
    "dfd91e60-6d31-f011-8c4e-6045bd1e9a24": "Credit card Crib Concerns",
    "5614a72a-6e31-f011-8c4e-6045bd1e9a24": "Credit Card excess payment transfer request",
    "2a52d3d1-0f62-f011-bec1-6045bd1dc2bf": "Credit Card fee reversal (NDI 90-240)",
    "d1e9320a-f735-f011-8c4d-6045bd1e9a24": "credit card fee reversal (NDIA 0-90)",
    "d2119744-6f31-f011-8c4e-6045bd1e9a24": "Credit card issued without consent",
    "a74a8296-7131-f011-8c4e-6045bd1e9a24": "Credit card limit downgrade request",
    "39dc5d1d-6d31-f011-8c4e-6045bd1e9a24": "Credit Card Limit Enhancement fee reversal - Temporary -",
    "f8f7896a-7131-f011-8c4e-6045bd1e9a24": "Credit card Limit enhancement request",
    "950a51e4-6e31-f011-8c4e-6045bd1e9a24": "Credit card loan on card request",
    "31c4caad-7661-f011-bec1-6045bd1dc2bf": "Credit card misselling",
    "1ee9bdd2-6f31-f011-8c4e-6045bd1e9a24": "Credit card NIC to EIC Changes",
    "fff6c2ae-7131-f011-8c4e-6045bd1e9a24": "Credit card not received",
    "67ae81f6-7131-f011-8c4e-6045bd1e9a24": "Credit card payment not been updated",
    "e4471e53-6d31-f011-8c4e-6045bd1e9a24": "Credit Card Pin re-issuance",
    "07e74ede-7131-f011-8c4e-6045bd1e9a24": "Credit card promotional discount not recieved",
    "fd241ad9-0936-f011-8c4d-6045bd1e9a24": "Credit card recent transactions cannot view in DFCC ONE",
    "00f7c2ae-7131-f011-8c4e-6045bd1e9a24": "Credit card redirection",
    "999abdf8-f635-f011-8c4d-6045bd1e9a24": "Credit card settlement plan  and letter issuance",
    "5e85c80f-6e31-f011-8c4e-6045bd1e9a24": "Credit card SMS alerts not recieved",
    "95f54c1c-6e31-f011-8c4e-6045bd1e9a24": "Credit card statement issue",
    "497d5290-6f31-f011-8c4e-6045bd1e9a24": "Credit card travel insuarance letter",
    "0d9d9f26-7231-f011-8c4e-6045bd1e9a24": "Credit card travel plan update request",
    "bdb3d003-6f31-f011-8c4e-6045bd1e9a24": "Credit card txn declined issue",
    "eb6f8802-0736-f011-8c4d-6045bd1e9a24": "Credit card unathorized txn",
    "0e9d9f26-7231-f011-8c4e-6045bd1e9a24": "Credit card unathorized txn",
    "aa1f5148-6e31-f011-8c4e-6045bd1e9a24": "Credit Early Renewal",
    "1f612314-0d62-f011-bec1-6045bd1dc2bf": "Crib clearance letter request",
    "bfa0622a-2b36-f011-8c4d-6045bd1e9a24": "CRM machine not working - DFCC ATM",
    "e1e0664c-2b36-f011-8c4d-6045bd1e9a24": "CRM machine not working - DFCC Offside ATM",
    "d80192ff-7561-f011-bec1-6045bd1dc2bf": "Customer cannot do bill payments - Joint Account",
    "122fdaf1-5a35-f011-8c4d-6045bd1e9a24": "Customer preposition Change Request",
    "32a19892-f935-f011-8c4d-6045bd1e9a24": "Daily limit enhansements requests",
    "0a20ee68-0636-f011-8c4d-6045bd1e9a24": "Debit card PIN not received",
    "958531f7-0536-f011-8c4d-6045bd1e9a24": "Debit card traval plan update requests",
    "d2708d92-2036-f011-8c4d-6045bd1e9a24": "DFCC One OTP issue",
    "0f2b67af-0d62-f011-bec1-6045bd1dc2bf": "Document Verification Request",
    "0e1d0210-5b35-f011-8c4d-6045bd1e9a24": "Dormant Account Activation",
    "ae47dd62-0e62-f011-bec1-6045bd1dc2bf": "Duplicate bill payments reversal",
    "dc69cd7f-0f62-f011-bec1-6045bd1dc2bf": "Duplicate bill payments reversal",
    "97d447f9-0936-f011-8c4d-6045bd1e9a24": "Email address not updated in DFCC One",
    "d6939286-0936-f011-8c4d-6045bd1e9a24": "Email address not updated in Online Banking",
    "1510c6a4-6b35-f011-8c4d-6045bd1e9a24": "FD Cancellation request",
    "a8c93626-6b35-f011-8c4d-6045bd1e9a24": "FD Renewel Request",
    "e9a39cd4-6a35-f011-8c4d-6045bd1e9a24": "FD Upliftment request",
    "805e21d9-6d31-f011-8c4e-6045bd1e9a24": "Fee & charges Reversal Request (OLF/LPF/INF)",
    "09596301-0836-f011-8c4d-6045bd1e9a24": "Fixed Deposit cannot open through the Online Banking",
    "99bc4e59-1162-f011-bec1-6045bd1dc2bf": "Foreign currency issuance request",
    "3febeb2f-5b35-f011-8c4d-6045bd1e9a24": "Foreign currency issuance request",
    "0c3b486d-6b35-f011-8c4d-6045bd1e9a24": "Fund hold release request",
    "68021e36-5b35-f011-8c4d-6045bd1e9a24": "Fund transfer Request",
    "3db3f851-1562-f011-bec1-6045bd1dc2bf": "Home branch change request",
    "fc41d770-2b36-f011-8c4d-6045bd1e9a24": "I CONNECT  Guidence Request",
    "7d462b93-2b36-f011-8c4d-6045bd1e9a24": "I CONNECT Login Error",
    "2fccae9b-2b36-f011-8c4d-6045bd1e9a24": "I CONNECT OTP Not Received",
    "92c8d78c-2b36-f011-8c4d-6045bd1e9a24": "I CONNECT Registation Support",
    "fab33c52-0e62-f011-bec1-6045bd1dc2bf": "Incorrect Bill payments",
    "ba3dedc2-0e62-f011-bec1-6045bd1dc2bf": "Incorrect Bill payments",
    "d597158e-7861-f011-bec1-6045bd1dc2bf": "Inward remittance inquiries",
    "36c56926-1162-f011-bec1-6045bd1dc2bf": "Inward/Outward CEFT Inquires  (Within DFCC)",
    "d85cd73f-1162-f011-bec1-6045bd1dc2bf": "Inward/Outward CEFT Inquires  (Within DFCC)",
    "7f1fbcda-7861-f011-bec1-6045bd1dc2bf": "Inward/Outward CEFT Inquires (Other Banks)",
    "e576bbf9-7861-f011-bec1-6045bd1dc2bf": "Inward/Outward CEFT Inquires (Other Banks)",
    "ea543fd6-7761-f011-bec1-6045bd1dc2bf": "IPG Inquiry",
    "20283be7-6d31-f011-8c4e-6045bd1e9a24": "IPP Related Requests",
    "702cc384-0636-f011-8c4d-6045bd1e9a24": "Issues with debit card account linkage",
    "2323c463-2536-f011-8c4d-6045bd1e9a24": "Leasing settlment plan requset",
    "fbf65148-5b35-f011-8c4d-6045bd1e9a24": "Letters for Inland Revenue request",
    "87606075-1562-f011-bec1-6045bd1dc2bf": "Limit reinstate/split request",
    "51193b0a-7761-f011-bec1-6045bd1dc2bf": "LIOC card cashback calculation concern",
    "540fd1e2-2236-f011-8c4d-6045bd1e9a24": "Loan processing dalays",
    "144d90f9-2236-f011-8c4d-6045bd1e9a24": "Loan settlment plan request",
    "126c7022-7761-f011-bec1-6045bd1dc2bf": "Lounge key and prority pass issue",
    "cd9d8396-2736-f011-8c4d-6045bd1e9a24": "Machine technical issues",
    "02674cff-1462-f011-bec1-6045bd1dc2bf": "New Account open request",
    "485b62df-1462-f011-bec1-6045bd1dc2bf": "New FD open request",
    "514c1b85-2736-f011-8c4d-6045bd1e9a24": "New Machine request",
    "09373cb5-0c62-f011-bec1-6045bd1dc2bf": "No arrears letter request",
    "e2a6ba81-5b35-f011-8c4d-6045bd1e9a24": "Nomination cancellation request",
    "99b129a3-5b35-f011-8c4d-6045bd1e9a24": "Nomination request",
    "2053c568-7661-f011-bec1-6045bd1dc2bf": "Online banking fee setup",
    "78916aa0-7661-f011-bec1-6045bd1dc2bf": "Online credit card application status",
    "a42b1c27-7661-f011-bec1-6045bd1dc2bf": "Online saving account opening inquirng",
    "5b78799c-7861-f011-bec1-6045bd1dc2bf": "Outward remittance inquiries",
    "93a50856-0936-f011-8c4d-6045bd1e9a24": "Past transactions cannot view in Online Banking",
    "38615341-5d35-f011-8c4d-6045bd1e9a24": "Pay Order request",
    "e35c85a2-2736-f011-8c4d-6045bd1e9a24": "Payment not credited",
    "3c8e3c94-6a35-f011-8c4d-6045bd1e9a24": "Poor Service",
    "152d1981-6b35-f011-8c4d-6045bd1e9a24": "POS machine chareges reversal request",
    "ae3264c4-7761-f011-bec1-6045bd1dc2bf": "POS Machine deployment",
    "61819bb3-7761-f011-bec1-6045bd1dc2bf": "POS Machine fee inquiry",
    "37c22bb4-6b35-f011-8c4d-6045bd1e9a24": "POS Machine Issues",
    "38c22bb4-6b35-f011-8c4d-6045bd1e9a24": "POS Machine Paper Rolls Request",
    "3702a2eb-7761-f011-bec1-6045bd1dc2bf": "POS machine payment reversal request",
    "5b2666ca-7761-f011-bec1-6045bd1dc2bf": "POS Machine removal",
    "c3e59192-7761-f011-bec1-6045bd1dc2bf": "POS machine settlement",
    "079ff8a8-7761-f011-bec1-6045bd1dc2bf": "POS machine surcharge concern",
    "64ae81f6-7131-f011-8c4e-6045bd1e9a24": "Promotion related cashback inquiries",
    "4388a7df-7761-f011-bec1-6045bd1dc2bf": "QR Inquiry",
    "02e17fd0-2036-f011-8c4d-6045bd1e9a24": "Request more details about the loan and the interest rates",
    "9dc470aa-6f31-f011-8c4e-6045bd1e9a24": "Request to change credit card billing cycle",
    "cc8240ff-0936-f011-8c4d-6045bd1e9a24": "Reset the password in DFCC One  but not received email",
    "e2b2205e-0936-f011-8c4d-6045bd1e9a24": "Reset the password in online banking  but not received email",
    "0bc3090c-7a61-f011-bec1-6045bd1dc2bf": "Retrieving data. Wait a few seconds and try to cut or copy again.",
    "3e14d1cd-7861-f011-bec1-6045bd1dc2bf": "RTGS inquiries",
    "8a5a6ded-0d62-f011-bec1-6045bd1dc2bf": "Service delivery related",
    "b597046c-6e31-f011-8c4e-6045bd1e9a24": "SMS Activation for the registered mobile",
    "a5b76716-6b35-f011-8c4d-6045bd1e9a24": "SMS Alert Cancellation request",
    "a12da02f-1562-f011-bec1-6045bd1dc2bf": "Special Foreign currency exchange rate request",
    "26956c0e-1562-f011-bec1-6045bd1dc2bf": "Special Interest rates request",
    "0d45ad70-5d35-f011-8c4d-6045bd1e9a24": "Standing order set up/ amendments & cancellations",
    "6b9289f5-6d31-f011-8c4e-6045bd1e9a24": "Statement copies Estatement / Paper",
    "94a50856-0936-f011-8c4d-6045bd1e9a24": "Statements downloading issue in Online Banking",
    "8f5f321b-7661-f011-bec1-6045bd1dc2bf": "Third party complaints on receiving sms alerts/emails",
    "753956ca-0b62-f011-bec1-6045bd1dc2bf": "Transaction confirmation letter request",
    "7bbd5022-0536-f011-8c4d-6045bd1e9a24": "Transaction confirmation letter requests",
    "e7202c03-6e31-f011-8c4e-6045bd1e9a24": "Transaction confirmation letters (To customs)",
    "dbd99426-f935-f011-8c4d-6045bd1e9a24": "Transaction declined issues",
    "e8b75208-2536-f011-8c4d-6045bd1e9a24": "Transaction receipt not received - DFCC ATM",
    "7d470b21-2536-f011-8c4d-6045bd1e9a24": "Transaction receipt not received - DFCC Offside ATM",
    "abd5addd-0c62-f011-bec1-6045bd1dc2bf": "Travel insurance letter request",
    "62f40948-0636-f011-8c4d-6045bd1e9a24": "TXN dispute and chargebacks",
    "add0e7f7-7231-f011-8c4e-6045bd1e9a24": "TXN dispute and chargebacks",
    "4fc59035-7661-f011-bec1-6045bd1dc2bf": "Unable to process online transactions - Joint Account",
    "ef1f5d4b-7661-f011-bec1-6045bd1dc2bf": "Unable to process online transactions DFCC ONE- Joint Account",
    "2eccae9b-2b36-f011-8c4d-6045bd1e9a24": "Unable to Reset Password and Username",
    "dcee1cf4-6a35-f011-8c4d-6045bd1e9a24": "Unauthorized Transaction on Savings Acc",
    "687f7aea-2336-f011-8c4d-6045bd1e9a24": "Unsuccessful ATM Withdrawal - Another bank ATM",
    "1b167c8c-2336-f011-8c4d-6045bd1e9a24": "Unsuccessful ATM Withdrawal - DFCC ATM",
    "c69ad3ae-2336-f011-8c4d-6045bd1e9a24": "Unsuccessful ATM Withdrawal - DFCC Offside ATM",
    "4eb880e7-2936-f011-8c4d-6045bd1e9a24": "Unsuccessful CRM Deposit - DFCC ATM",
    "801fd710-2a36-f011-8c4d-6045bd1e9a24": "Unsuccessful CRM Deposit - DFCC Offside ATM",
    "656ee724-2a36-f011-8c4d-6045bd1e9a24": "Unsuccessful CRM Withdrawal - DFCC ATM",
    "a572043b-2a36-f011-8c4d-6045bd1e9a24": "Unsuccessful CRM Withdrawal - DFCC Offside ATM",
    "7c1c2333-0d62-f011-bec1-6045bd1dc2bf": "VISA confirmation letter request",
    "0e146444-1562-f011-bec1-6045bd1dc2bf": "VISA confirmation letter request",
    "287eefa3-7861-f011-bec1-6045bd1dc2bf": "Worker remmitance inquiries",
}

BRANCH_MAP = {
    "38d39371-9f42-f011-877a-6045bd1e9a24": "AGALAWATTA BRANCH",
    "265b5677-9e42-f011-877a-6045bd1e9a24": "AKKARAIPATTU BRANCH",
    "b9a36a65-9e42-f011-877a-6045bd1e9a24": "AKURESSA BRANCH",
    "9350edb9-9f42-f011-877a-6045bd1e9a24": "ALUTHGAMA BRANCH",
    "81307ac2-9d42-f011-877a-6045bd1e9a24": "AMBALANGODA BRANCH",
    "540caa14-9f42-f011-877a-6045bd1e9a24": "AMBALANTOTA BRANCH",
    "26659eca-9d42-f011-877a-6045bd1e9a24": "AMPARA BRANCH",
    "f68aeed0-9c42-f011-877a-6045bd1e9a24": "ANURADHAPURA BRANCH",
    "6ee2bae9-9e42-f011-877a-6045bd1e9a24": "ARALAGANWILA BRANCH",
    "baa36a65-9e42-f011-877a-6045bd1e9a24": "ARAYAMPATHY BRANCH (KATHTHANKUDY)",
    "37d39371-9f42-f011-877a-6045bd1e9a24": "ATHURUGIRIYA BRANCH",
    "99307ac2-9d42-f011-877a-6045bd1e9a24": "AVISSAWELLA BRANCH",
    "ad22de2c-9f42-f011-877a-6045bd1e9a24": "BADDEGAMA BRANCH",
    "bedcf4df-9c42-f011-877a-6045bd1e9a24": "BADULLA BRANCH",
    "00edd48f-9f42-f011-877a-6045bd1e9a24": "BADURALIYA BRANCH",
    "75f7fbcf-9e42-f011-877a-6045bd1e9a24": "BALANGODA BRANCH",
    "301ee5d9-9e42-f011-877a-6045bd1e9a24": "BANDARAGAMA BRANCH",
    "8e8c4708-9d42-f011-877a-6045bd1e9a24": "BANDARANAYAKE MW BRANCH",
    "38d24633-9d42-f011-877a-6045bd1e9a24": "BANDARAWELA BRANCH",
    "25659eca-9d42-f011-877a-6045bd1e9a24": "BATTICALOA BRANCH",
    "009f0e79-9f42-f011-877a-6045bd1e9a24": "BELIATTA BRANCH",
    "3b5ba696-9f42-f011-877a-6045bd1e9a24": "BIBILE BRANCH",
    "1086fcec-9c42-f011-877a-6045bd1e9a24": "BORELLA BRANCH",
    "3f6d413c-9f42-f011-877a-6045bd1e9a24": "BUTTALA BRANCH",
    "b6447aa9-9d42-f011-877a-6045bd1e9a24": "CHILAW BRANCH",
    "285b5677-9e42-f011-877a-6045bd1e9a24": "CHUNNAKAM BRANCH",
    "24f940c1-9c42-f011-877a-6045bd1e9a24": "CITY OFFICE BRANCH",
    "fa2bd956-9d42-f011-877a-6045bd1e9a24": "DAMBULLA BRANCH",
    "eaf6620b-9f42-f011-877a-6045bd1e9a24": "DANKOTUWA BRANCH",
    "9c9d22e0-9e42-f011-877a-6045bd1e9a24": "DEHIATTAKANDIYA BRANCH",
    "70e85489-9d42-f011-877a-6045bd1e9a24": "DENIYAYA BRANCH",
    "a6dc7790-9e42-f011-877a-6045bd1e9a24": "DIGANA BRANCH",
    "1719bb89-9f42-f011-877a-6045bd1e9a24": "DIKWELLA BRANCH",
    "d7889a9f-9e42-f011-877a-6045bd1e9a24": "EHELIYAGODA BRANCH",
    "19cb3c5a-9e42-f011-877a-6045bd1e9a24": "ELPITIYA BRANCH",
    "58134ed9-9d42-f011-877a-6045bd1e9a24": "EMBILIPITIYA BRANCH",
    "fdcf5444-9f42-f011-877a-6045bd1e9a24": "EPPAWALA BRANCH",
    "bc81ce61-9f42-f011-877a-6045bd1e9a24": "FORT SUPER GRADE BRANCH",
    "b1c60897-9e42-f011-877a-6045bd1e9a24": "GALEWELA BRANCH",
    "ad2d7cb2-9d42-f011-877a-6045bd1e9a24": "GALLE BRANCH",
    "a7d7e7d8-9c42-f011-877a-6045bd1e9a24": "GAMPAHA BRANCH",
    "0d6319a2-9d42-f011-877a-6045bd1e9a24": "GAMPOLA BRANCH",
    "08a18bbe-9e42-f011-877a-6045bd1e9a24": "GANGODAWILA BRANCH",
    "a4018af8-9e42-f011-877a-6045bd1e9a24": "GIRIULLA BRANCH",
    "83ea2258-9f42-f011-877a-6045bd1e9a24": "GODAKAWELA BRANCH",
    "f57c15b2-9f42-f011-877a-6045bd1e9a24": "HAKMANA BRANCH",
    "f41ad788-9e42-f011-877a-6045bd1e9a24": "HAMBANTOTA BRANCH",
    "ce66afab-9f42-f011-877a-6045bd1e9a24": "HAPUTALE BRANCH",
    "6e4857b0-9e42-f011-877a-6045bd1e9a24": "HATTON BRANCH",
    "4e73af01-9f42-f011-877a-6045bd1e9a24": "HIKKADUWA BRANCH",
    "74f7fbcf-9e42-f011-877a-6045bd1e9a24": "HINGURAKGODA BRANCH",
    "d448b9a4-9f42-f011-877a-6045bd1e9a24": "HOMAGAMA BRANCH",
    "ac2d7cb2-9d42-f011-877a-6045bd1e9a24": "HORANA BRANCH",
    "9bfef8b6-9e42-f011-877a-6045bd1e9a24": "IBBAGAMUWA BRANCH",
    "f51ad788-9e42-f011-877a-6045bd1e9a24": "JA-ELA BRANCH",
    "01d3ebd1-9d42-f011-877a-6045bd1e9a24": "JAFFNA BRANCH",
    "3dcb7798-9d42-f011-877a-6045bd1e9a24": "KADAWATHA BRANCH",
    "4aea6f00-9d42-f011-877a-6045bd1e9a24": "KADURUWELA BRANCH",
    "c0f097c4-9e42-f011-877a-6045bd1e9a24": "KADUWELA BRANCH",
    "ed44f4f1-9e42-f011-877a-6045bd1e9a24": "KAHAWATTA BRANCH",
    "dc9431bb-9d42-f011-877a-6045bd1e9a24": "KALAWANA BRANCH",
    "38cd94f0-9d42-f011-877a-6045bd1e9a24": "KALMUNAI BRANCH",
    "473eaf8f-9d42-f011-877a-6045bd1e9a24": "KALUTARA BRANCH",
    "24a464b9-9c42-f011-877a-6045bd1e9a24": "KANDY",
    "9b9d22e0-9e42-f011-877a-6045bd1e9a24": "KANDY CITY CENTRE BRANCH",
    "3f68e27f-9f42-f011-877a-6045bd1e9a24": "KARANDENIYA BRANCH",
    "6c93f5e6-9d42-f011-877a-6045bd1e9a24": "KATUGASTOTA BRANCH",
    "6d93f5e6-9d42-f011-877a-6045bd1e9a24": "KEGALLE BRANCH",
    "171ce469-9f42-f011-877a-6045bd1e9a24": "KEKIRAWA BRANCH",
    "497308f8-9d42-f011-877a-6045bd1e9a24": "KILINOCHCHI BRANCH",
    "4b3eaf8f-9d42-f011-877a-6045bd1e9a24": "KIRIBATHGODA BRANCH",
    "8c018af8-9e42-f011-877a-6045bd1e9a24": "KOCHCHIKADE BRANCH",
    "a5dc7790-9e42-f011-877a-6045bd1e9a24": "KOTAHENA BRANCH",
    "2bfc1d47-9d42-f011-877a-6045bd1e9a24": "KOTTAWA BRANCH",
    "9250edb9-9f42-f011-877a-6045bd1e9a24": "KOTTEGODA BRANCH",
    "a912a267-9d42-f011-877a-6045bd1e9a24": "KULIYAPITIYA BRANCH",
    "36f182b0-9c42-f011-877a-6045bd1e9a24": "KURUNEGALA BRANCH",
    "bd81ce61-9f42-f011-877a-6045bd1e9a24": "KURUWITA BRANCH",
    "019f0e79-9f42-f011-877a-6045bd1e9a24": "MAHA OYA BRANCH",
    "bf42f412-9d42-f011-877a-6045bd1e9a24": "MAHARAGAMA BRANCH",
    "84ea2258-9f42-f011-877a-6045bd1e9a24": "MAHIYANGANAYA BRANCH",
    "4870029f-9c42-f011-877a-6045bd1e9a24": "MALABE BRANCH",
    "3a010580-9e42-f011-877a-6045bd1e9a24": "MANIPAY BRANCH",
    "8089f64a-9f42-f011-877a-6045bd1e9a24": "MARAWILA BRANCH",
    "0e6319a2-9d42-f011-877a-6045bd1e9a24": "MATALE BRANCH",
    "db22cba7-9c42-f011-877a-6045bd1e9a24": "MATARA BRANCH",
    "b19fa734-9f42-f011-877a-6045bd1e9a24": "MATARA CITY BRANCH",
    "d8889a9f-9e42-f011-877a-6045bd1e9a24": "MATUGAMA BRANCH",
    "8189f64a-9f42-f011-877a-6045bd1e9a24": "MAWANELLA BRANCH",
    "6fe2bae9-9e42-f011-877a-6045bd1e9a24": "MEDIRIGIRIYA BRANCH",
    "181ce469-9f42-f011-877a-6045bd1e9a24": "MINUWANGODA BRANCH",
    "37cd94f0-9d42-f011-877a-6045bd1e9a24": "MONARAGALA BRANCH",
    "02d3ebd1-9d42-f011-877a-6045bd1e9a24": "MORATUWA BRANCH",
    "ac22de2c-9f42-f011-877a-6045bd1e9a24": "MORAWAKA BRANCH",
    "6d4857b0-9e42-f011-877a-6045bd1e9a24": "MT. LAVINIA BRANCH",
    "3075cff7-9c42-f011-877a-6045bd1e9a24": "NARAHENPITA EXT OFFICE",
    "ae6a0da8-9e42-f011-877a-6045bd1e9a24": "NARAMMALA BRANCH",
    "cd66afab-9f42-f011-877a-6045bd1e9a24": "NAULA BRANCH",
    "3ccb7798-9d42-f011-877a-6045bd1e9a24": "NAWALA",
    "e9f6620b-9f42-f011-877a-6045bd1e9a24": "NAWALAPITIYA BRANCH",
    "cd9ead3e-9d42-f011-877a-6045bd1e9a24": "NEGOMBO BRANCH",
    "3b010580-9e42-f011-877a-6045bd1e9a24": "NELLIADY BRANCH",
    "af6a0da8-9e42-f011-877a-6045bd1e9a24": "NIKAWERATIYA BRANCH",
    "b29fa734-9f42-f011-877a-6045bd1e9a24": "NIVITHIGALA BRANCH",
    "ac645496-9c42-f011-877a-6045bd1e9a24": "NUGEGODA BRANCH",
    "db9431bb-9d42-f011-877a-6045bd1e9a24": "NUWARA ELIYA BRANCH",
    "9903fa6d-9e42-f011-877a-6045bd1e9a24": "ODDAMAVADI BRANCH",
    "e36ed06e-9d42-f011-877a-6045bd1e9a24": "PANADURA BRANCH",
    "311ee5d9-9e42-f011-877a-6045bd1e9a24": "PERADENIYA BRANCH",
    "ec44f4f1-9e42-f011-877a-6045bd1e9a24": "PETTAH MAIN STREET BRANCH",
    "dd6daee0-9d42-f011-877a-6045bd1e9a24": "PETTAH PEOPLES PARK BRANCH",
    "f44e7f79-9d42-f011-877a-6045bd1e9a24": "PILIYANDALA BRANCH",
    "892e08db-9f42-f011-877a-6045bd1e9a24": "PINNACLE CENTER",
    "23f705ca-9f42-f011-877a-6045bd1e9a24": "PUTTALAM BRANCH",
    "544be880-9c42-f011-877a-6045bd1e9a24": "RAMANAYAKE MW BRANCH",
    "44fab09d-9f42-f011-877a-6045bd1e9a24": "RAMBUKKANA BRANCH",
    "642ec5c8-9c42-f011-877a-6045bd1e9a24": "RATNAPURA BRANCH",
    "43fab09d-9f42-f011-877a-6045bd1e9a24": "RATTOTA BRANCH",
    "2877e251-9f42-f011-877a-6045bd1e9a24": "RUWANWELLA BRANCH",
    "9803fa6d-9e42-f011-877a-6045bd1e9a24": "TANGALLE BRANCH",
    "b0c60897-9e42-f011-877a-6045bd1e9a24": "THAMBUTTEGAMA BRANCH",
    "aa73b91e-9f42-f011-877a-6045bd1e9a24": "TISSAMAHARAMA BRANCH",
    "57134ed9-9d42-f011-877a-6045bd1e9a24": "TRINCOMALEE BRANCH",
    "3e68e27f-9f42-f011-877a-6045bd1e9a24": "UHANA BRANCH",
    "4d5659c2-9f42-f011-877a-6045bd1e9a24": "URAGASMANHANDIYA BRANCH",
    "3e6d413c-9f42-f011-877a-6045bd1e9a24": "URUBOKKA BRANCH",
    "de6daee0-9d42-f011-877a-6045bd1e9a24": "VAVUNIYA BRANCH",
    "1c19bb89-9f42-f011-877a-6045bd1e9a24": "VEYANGODA BRANCH",
    "3c5ba696-9f42-f011-877a-6045bd1e9a24": "WARAKAPOLA BRANCH",
    "4e5659c2-9f42-f011-877a-6045bd1e9a24": "WATHUGEDARA BRANCH",
    "ebf6575f-9d42-f011-877a-6045bd1e9a24": "WATTALA BRANCH",
    "550caa14-9f42-f011-877a-6045bd1e9a24": "WATTEGAMA BRANCH",
    "bff097c4-9e42-f011-877a-6045bd1e9a24": "WELIGAMA",
    "d548b9a4-9f42-f011-877a-6045bd1e9a24": "WELIKANDA BRANCH",
    "93fef8b6-9e42-f011-877a-6045bd1e9a24": "WELIMADA BRANCH",
    "b7447aa9-9d42-f011-877a-6045bd1e9a24": "WELLAWATTE BRANCH",
    "fccf5444-9f42-f011-877a-6045bd1e9a24": "WELLAWAYA BRANCH",
    "4d73af01-9f42-f011-877a-6045bd1e9a24": "WENNAPPUWA BRANCH",
}

TICKET_TYPE_MAP = {
    "0" : "Complaint",
    "1" : "Request",
    "2" : "Inquiry",
    "3" : "Sales Lead",
}

TICKET_RECEIVED_THROUGH_MAP = {
    "0" : "Call Centre",
    "1" : "Care Centre",
    "2" : "Secure Mail",
    "3" : "FCRD",
    "4" : "CEO Escalation",
    "5" : "Escalation",
    "6" : "Social Media",
    "7" : "Branch",
    "8" : "Other"
}

ACTIVE_STATUS_MAP = {
    "0" : "Closed",
    "1" : "Active"
}

CLAIMING_STATUS_MAP = {
    "0" : "UnClaimed",
    "1" : "Accepted"
} 






TARGET_COLUMNS = {
    "cr1f8_departments": DEPT_MAP,
    "cr1f8_product": PRODUCT_MAP,
    "cr1f8_sla_days": SLA_MAP,
    "cr1f8_complaint_titles": COMPLAINT_TITLES_MAP,
    "cr1f8_branch": BRANCH_MAP,
    "cr1f8_complain_title": TICKET_TYPE_MAP,
    "cr1f8_channel" : TICKET_RECEIVED_THROUGH_MAP,
    "cr1f8_activestatus" : ACTIVE_STATUS_MAP,
    "cr1f8_claimingstatus" : CLAIMING_STATUS_MAP
}

def normalize(val: str) -> str:
    """Trim and lowercase value for matching while preserving original strings."""
    if pd.isna(val):
        return val
    return str(val).strip().lower()

def replace_with_map(series: pd.Series, value_map: dict) -> tuple[pd.Series, int]:
    """Replace values found in value_map (matching case-insensitively) and return count replaced."""
    # Build a normalized lookup (lowercase keys)
    norm_map = {k.lower(): v for k, v in value_map.items()}
    # Compute mask of rows to replace
    original = series.astype("string")
    norm_vals = original.map(normalize)
    mask = norm_vals.isin(norm_map.keys())
    replaced = original.where(~mask, norm_vals.map(norm_map))
    changed = int(mask.sum())
    return replaced, changed

def main():
    ap = argparse.ArgumentParser(description="Replace hashed GUIDs in CSV columns with readable text.")
    ap.add_argument("--in", dest="inp", required=True, help="Input CSV path")
    ap.add_argument("--out", dest="out", required=True, help="Output CSV path")
    ap.add_argument("--sep", default=",", help="CSV delimiter (default ,)")
    ap.add_argument("--encoding", default="utf-8", help="File encoding (default utf-8)")
    ap.add_argument("--backup", action="store_true", help="Backup the original CSV as <input>.bak.csv")
    ap.add_argument("--dry-run", action="store_true", help="Show summary only; don't write output file")
    args = ap.parse_args()

    inp = Path(args.inp)
    outp = Path(args.out)

    if not inp.exists():
        print(f"[ERROR] Input file not found: {inp}", file=sys.stderr)
        sys.exit(1)

    if args.backup:
        backup_path = inp.with_suffix(inp.suffix + ".bak.csv")
        shutil.copyfile(inp, backup_path)
        print(f"[INFO] Backup saved -> {backup_path}")

    # Read CSV (keep everything as string to avoid GUID corruption)
    try:
        df = pd.read_csv(inp, dtype=str, sep=args.sep, encoding=args.encoding, keep_default_na=False)
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}", file=sys.stderr)
        sys.exit(1)

    total_changes = 0
    for col, mapping in TARGET_COLUMNS.items():
        if col in df.columns:
            new_series, changed = replace_with_map(df[col], mapping)
            df[col] = new_series
            print(f"[OK] Column '{col}': {changed} value(s) replaced")
            total_changes += changed
        else:
            print(f"[SKIP] Column '{col}' not found in CSV")

    print(f"[SUMMARY] Total replacements: {total_changes}")
    if args.dry_run:
        print("[DRY-RUN] No file written")
        return

    # Write output CSV (use lineterminator for wider pandas compatibility)
    try:
        df.to_csv(outp, index=False, sep=args.sep, encoding=args.encoding, lineterminator="\n")
        print(f"[DONE] Wrote updated CSV -> {outp}")
    except TypeError as e:
        # Fallback for very old pandas that might not accept lineterminator either
        print(f"[WARN] pandas 'lineterminator' not supported ({e}); writing without it.")
        df.to_csv(outp, index=False, sep=args.sep, encoding=args.encoding)
        print(f"[DONE] Wrote updated CSV -> {outp} (default line endings)")
    except Exception as e:
        print(f"[ERROR] Failed to write CSV: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

