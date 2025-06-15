from curses import termattrs
import streamlit
import re

class LoanCalculator:
    
    def __init__(self, sl:streamlit=None):
        if not sl:
            sl = streamlit
            
        self.sl = sl
        self.sl.text_input("Loan Amount ($)", key='loanamount')
        if 'loanterm' not in self.sl.session_state:
            self.sl.session_state.loanterm = '' 
        if 'loanconditions' not in self.sl.session_state:
            self.sl.session_state.loanconditions = []
        
        if 'loanfind' not in self.sl.session_state:
            self.sl.session_state.loanfind = None
        if 'loanpayment' not in self.sl.session_state:
            self.sl.session_state.loanpayment = None
            
        value = self.sl.text_input("Loan Term (months)", value=self.sl.session_state.loanterm)
        if value:
            if re.search(r'[^0-9]', value):
                calculatedval = eval(value)
                self.sl.session_state.loanterm = calculatedval
                self.sl.rerun()
            else:
                self.sl.session_state.loanterm = value
            
        self.sl.text_input("Interest Rate (%)", key='loaninterest')
        
        self.sl.radio(
            'Compound', 
            options=[
                'Yearly',
                'Semiannually',
                'Quarterly',
                'Monthly',
                'Biweekly',
                'Weekly',
                'Daily'
            ], 
            index=3,
            key='loancompound',
            horizontal=True
        )
        
        print(f'Find {self.sl.session_state.loanfind}')
        
        if 'loanfind' in self.sl.session_state:
            if self.sl.session_state.loanfind == 'Total Amount':
                self.sl.text_input("Periodic Payment", key='loanpayment')
            elif self.sl.session_state.loanfind == 'Additional Principal':
                self.sl.text_input("Periodic Payment", key='loanpayment')
                self.sl.text_input("Total Amount", key='loantotal')
            elif self.sl.session_state.loanfind == 'Terms To Payoff':
                self.sl.text_input('Periodic Payment', key='loanpayment')
        
        self.sl.session_state.loanconditionoptions = [
                                                    'Initial Payment (Per Pay Period)',
                                                    'Additional Principal (One Time)',
                                                    'Additional Principal (Per Pay Period)'
                                                ]
        if 'loanconditiontype' not in self.sl.session_state:
            self.sl.session_state.loanconditiontype = None
        if 'loanconditionamount' not in self.sl.session_state:
            self.sl.session_state.loanconditionamount = None
        
        print(f'Conditions {self.sl.session_state.loanconditions}')
        #Display added conditions
        if self.sl.session_state.loanconditions:
            i = 0
            for condition in self.sl.session_state.loanconditions:
                cols = self.sl.columns([1, 10]) 
                with cols[0]:
                    if self.sl.button('x', key=f'loancondition{i}'):
                        print(f' Remove condition {condition[0]}')
                        self.sl.session_state.loanconditions.remove(condition)
                        self.sl.rerun()
                    i += 1
                with cols[1]:
                    print(f'  Condition {condition[0]} {condition[1]}')
                    if len(condition) == 2:
                        self.sl.write(f'{condition[0]}: {condition[1]}')
                    elif len(condition) == 3:
                        self.sl.write(f'{condition[0]}: {condition[1]} on {condition[2]}th pay period')
        
        #Display unfinished conditions.
        #Each time a field changed, redrawn happens so each ui needs to be redrawn.
        if self.sl.session_state.loanconditiontype:
            cols = self.sl.columns([4,2,2])
            with cols[0]:
                cond = self.sl.selectbox(
                        "Select Condition Type", 
                        options=self.sl.session_state.loanconditionoptions,
                        index=self.sl.session_state.loanconditionoptions.index(self.sl.session_state.loanconditiontype))
                if cond:
                    self.sl.session_state.loanconditiontype = cond
            with cols[1]:
                if self.sl.session_state.loanconditionamount:
                    amount = self.sl.text_input('Amount', value=self.sl.session_state.loanconditionamount)
                else:
                    amount = self.sl.text_input('Amount')
                    if amount:
                        if self.sl.session_state.loanconditiontype == self.sl.session_state.loanconditionoptions[1]: #Additional principal at a specified period
                            self.sl.session_state.loanconditionamount = amount
                        #Additional principal per pay period or initial payment per period
                        else:
                            print(f'Add new conditions: {self.sl.session_state.loanconditiontype} {amount}')
                            self.sl.session_state.loanconditions.append([self.sl.session_state.loanconditiontype, amount])
                            self.sl.session_state.loanconditiontype = None
                            self.sl.rerun()
            with cols[2]:
                if self.sl.session_state.loanconditiontype == self.sl.session_state.loanconditionoptions[1] and self.sl.session_state.loanconditionamount: 
                    when = self.sl.text_input('On Pay Period')
                    if when:
                        print(f'Add new conditions: {self.sl.session_state.loanconditiontype} {self.sl.session_state.loanconditionamount} {when}')
                        self.sl.session_state.loanconditions.append([self.sl.session_state.loanconditiontype, self.sl.session_state.loanconditionamount, when])
                        self.sl.session_state.loanconditiontype = None
                        self.sl.session_state.loanconditionamount = None
                        self.sl.rerun()                         

        
        if self.sl.button("More Conditions", help="Add additional conditions", key='loancondition'):  
            cond = self.sl.selectbox(
                "Select Condition Type", 
                options=self.sl.session_state.loanconditionoptions,
                index=None,
                key='loanconditiontype',
                placeholder="Select Condition")
            print(f'Selected {cond}')
            if cond:
                self.sl.session_state.loanconditiontype = cond 
            
        
        
        print(f'{sl.session_state.loanamount} {sl.session_state.loanterm} {sl.session_state.loaninterest}')
        cols = self.sl.columns(2)
        with cols[0]:
            self.sl.selectbox(
                "Find", 
                options=[
                    'Periodic Payment',
                    'Total Amount',
                    'Terms To Payoff'
                    ],
                key='loanfind')
        
        ret = None
        with cols[1]:
            self.sl.write('')
            self.sl.write('')
            if sl.session_state.loanamount and sl.session_state.loanterm and sl.session_state.loaninterest:
                if self.sl.session_state.loanconditions:
                    #Check to make sure the additional conditions don't conflict with what we try to calculate
                    if self.sl.session_state.loanfind == 'Periodic Payment' and any('Additional Principal (Per Pay Period)' in tup for tup in self.sl.session_state.loanconditions):
                        self.sl.error('Cannot find Periodic Payment with with addition of principal per pay period in conditions.  Try Total Amount or Terms to Payoff')
                    elif self.sl.session_state.loanfind == 'Additional Principal' and (any('Additional Principal (Per Pay Period)' in tup for tup in self.sl.session_state.loanconditions) or any('Additional Principal (One Time)' in tup for tup in self.sl.session_state.loanconditions)):
                        self.sl.error('Cannot find Additional Principal with with addition of principals in conditions.  Try Total Amount or Terms to Payoff')
                    
                    else:
                        ok = True
                else:
                    ok = True
                if self.sl.button("Calculate", key='loancalculate'):
                    conditions = self.sl.session_state.loanconditions.copy()
                    ret = self.calculate(sl.session_state.loanamount, 
                                        sl.session_state.loanterm, 
                                        sl.session_state.loaninterest, 
                                        sl.session_state.loancompound,
                                        sl.session_state.loanpayment,
                                        self.sl.session_state.loanfind, 
                                        conditions)
        if ret:
            if self.sl.session_state.loanfind == 'Periodic Payment':
                if isinstance(ret, list):
                    self.sl.write("Periodic Payment:")
                    total = 0
                    for item in ret:
                        self.sl.write(f'{item[0]} for pay period {item[1]} to {item[2]}')
                        total += item[0] * (int(item[2])-int(item[1])+1)
                    self.sl.write(f'Total payment at the end of loan: {total}')
                else:
                    self.sl.write(f"Periodic Payment: ${ret}")
            elif self.sl.session_state.loanfind == 'Total Amount':
                self.sl.write(f"Total Amount: ${ret}")
            elif self.sl.session_state.loanfind == 'Terms To Payoff':
                self.sl.write(f'The Number of Terms to Payoff: {ret}')
            
    def calculate(self, loanamount, loanterm, loaninterest, loancompound, loanpayment, loanfind, conditions=None):
        P = float(loanamount)
        t = float(loanterm)
        i = float(loaninterest)/100
        
        #Compound
        n = {
            'yearly': 1,
            'semiannually': 2,
            'quarterly':4,
            'monthly': 12,
            'biweekly':26,
            'weekly': 52,
            'daily':365
        }
        # Interest per pay period
        i = i / n[loancompound.lower()]
        
        if loanfind == 'Periodic Payment':
            if conditions and conditions[0][0] == 'Initial Payment (Per Pay Period)':
                payment = int(conditions[0][1])
                conditions.remove(conditions[0])
            else:
                payment = self.calculate_periodic_payment(P, t, i)
            payments = [(payment, 1, loanterm)]
            if conditions:
                payment1 = payment
                for condition in conditions: 
                    if condition[0] == 'Additional Principal (One Time)':
                        payperiod = int(condition[2])
                        for r in range(1, payperiod):
                            P += i * P
                            #print(f'Total P={P} with interest {i} at period {r}')
                            P -= payment1
                            #print(f'Total P={P} with payment {payment1} at period {r}')
                        P -= int(condition[1]) 
                        t -= payperiod-1
                        print(f'New numbers at {payperiod}: P={P} t={t}')
                        payment1 = self.calculate_periodic_payment(P, t, i)
                        lastidx = len(payments) -1
                        lastpayment = list(payments[lastidx])
                        lastpayment[2]=payperiod-1
                        payments[lastidx] = tuple(lastpayment)
                        payments.append((payment1, payperiod, loanterm))
            return payments
        elif loanfind == 'Total Amount':
            return self.calculate_total_amount(P, t, i)
        elif loanfind == 'Terms To Payoff':
            return self.calculate_terms(P, t, i, float(loanpayment))
        return f"Error: {loanfind} Not supported"
    
    def calculate_periodic_payment(self, loanamount, loanterm, loaninterest):
        #Formula: p= (i x P) / (1 - (1 + i)^-n), p = monthly payment, i = interest per pay period, n = number of periods, P = loan amount (principal)
        # Note interest per pay period = annual interest / # of pay periods per year
        # Alternative formula: Periodic loan payment = Loan amount / (((1 + Periodic rate) ^ Number of payments) - 1) / (Periodic rate × ((1 + Periodic rate) ^ Number of payments))
        payment = (loaninterest * loanamount) / (1 - (1+loaninterest)**-loanterm)
        return payment
        
    def calculate_total_amount(self, loanamount, loanterm, loaninterest):
        # total amount = periodic payment x number of payments
        payment = self.calculate_periodic_payment(loanamount, loanterm, loaninterest)
        total = payment * loanterm
        return total
        
        
    def calculate_terms(self, loanamount, loanterm, loaninterest, payment):
        #Derive from: p= (i x P) / (1 - (1 + i)^-n), p = monthly payment, i = interest per pay period, n = number of periods, P = loan amount (principal)
        # 1/ (1 - (i*P)/p) = (1+i)^n
        
        left = 1 / (1 - (loaninterest * loanamount)/payment)
        right = 1+loaninterest
        initialn = int(loanterm)
        low = left + 10
        while low > left:
            low = (1+loaninterest) ** initialn
            initialn = int(initialn * 2 / 3)
        if low < left:
            while low < left:
                low = (1+loaninterest) ** initialn
                initialn +=1
            initialn -= 1
        return initialn
    