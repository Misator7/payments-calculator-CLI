#!/usr/bin/env python 

import os
from Color import *

class a:
    id = 0
    run = True
    fileName = ""
    openMode = False
    entities = dict()
    records = dict()
    groups = dict()

    def __init__(self):
        self.KEYWORDS = {
            "add" : self.AddRecord,
            "rm"  : self.Remove,
            "evl" : self.Evaluate,
            "rec" : self.Records,
            "agr" : self.AddGroup,
            "dgr" : self.DeleteGroup,
            "lgr" : self.ListGroups,
            "imp" : self.Import,
            "exp" : self.Export,
            "opn" : self.Open,
            "cls" : self.Close,
            "rs"  : self.Reset,
            "save": self.Save,
            "help": self.Help,
            "exit": self.Exit
        }
        self.HELP = [
            ["add" , "adding record -> add [payer] [amount] [debtor1] [debtor2] [...]"],
            ["rm"  , "remove record -> rm [id]"],
            ["evl" , "show evaluation"],
            ["rec" , "show records"],
            ["agr" , "add group -> agr [groupName] [member1] [member2] [...]"],
            ["rgr" , "remove group -> rgr [groupName]"],
            ["lgr" , "list of groups"],
            ["imp" , "import records -> imp [fileName]"],
            ["exp" , "export records -> exp [fileName]"],
            ["opn" , "open file -> opn [FileName]"],
            ["cls" , "close opened file"],
            ["rs"  , "delete all records"],
            ["save", "save evaluation and records table -> save [fileName]"],
            ["help", "show list of commands"],
            ["exit", "exit from app"]
        ]

    def Add(self, payer : str, debtors : list, amount : int):
        sign = 1
        if amount < 0:
            sign = -1
        if payer not in self.entities:
                self.entities[payer] = [1,amount]
        else:
            self.entities[payer] = [self.entities[payer][0] + sign, self.entities[payer][1] + amount]
            if self.entities[payer][0] == 0:
                del self.entities[payer]
        n = amount / len(debtors)
        for debtor in debtors:
            if debtor not in self.entities:
                self.entities[debtor] = [1, -n]
            else:
                self.entities[debtor] = [self.entities[debtor][0] + sign, self.entities[debtor][1] - n]
                if self.entities[debtor][0] == 0:
                    del self.entities[debtor]

    def RecordToStr(self, cmd):
        line = ""
        for i in cmd:
            line += i+" "
        return line

    def AddRecord(self, cmd):
        debtors = list()
        for i in cmd[3:]:
            if i in self.groups:
                debtors = debtors + self.groups[i]
            else:
                debtors.append(i)
        self.Add(cmd[1], debtors, int(cmd[2]))
        self.id += 1
        self.records[str(self.id)] = cmd[:3] + debtors
        if self.openMode:
            try:
                f = open(self.fileName, "a", encoding="utf-8")
                f.write(self.RecordToStr(cmd))
                f.close()
            except FileNotFoundError:
                print(f"{Color.RED}File not found!{Color.ENDC}")

    def Remove(self, cmd):
        if cmd[1] not in self.records:
            print(f"{Color.RED}\"{cmd[1]}\" does not exist!{Color.ENDC}")
        else:
            record = self.records.pop(cmd[1])
            print("\""+Color.SYS+self.RecordToStr(record)+Color.ENDC+"\"", end=" ")
            record[1] = "-" + record[1]
            self.Add(record[1], record[3:], int(record[2]))
            print(f"{Color.GREEN}Succesfully deleted{Color.ENDC}")
            if self.openMode:
                try:
                    f = open(self.fileName, "w", encoding="utf-8")
                    for r in self.records.values():
                        f.write(self.RecordToStr(r)+"\n")
                    f.close()
                except FileNotFoundError:
                    print(f"{Color.RED}File not found!{Color.ENDC}")
        
    def Evaluate(self, cmd):
        dash = lambda n : print(n * "-")
        print()
        dash(26)
        print('{:<15}|{:>10}'.format("Name","Amount"))
        dash(26)
        for i in self.entities.keys():
            x = round(self.entities[i][1],2) + 0
            color = Color.GREEN
            if x < 0:
                color = Color.RED
            print('{:<15}|{:>19}'.format(i, f"{color}{'{:.2f}'.format(x)}{Color.ENDC}"))
        print()

    def Records(self, cmd):
        dash = lambda n : print(n*"-")
        print()
        dash(47)
        print('{:<4}| {:<10}| {:<15}| {:<15}'.format("id","amount","payer", "debtor(s)"))
        dash(47)
        for r in self.records:
            rec = self.records[r]
            print('{:<4}| {:<10}| {:<15}|'.format(r, rec[2], rec[1]), rec[3],end="")
            for i in range(4,len(rec)):
                print(f", {rec[i]}",end="")
            print()
        print(f"records: {len(self.records)}")
        print()

    def AddGroup(self, cmd):
        self.groups[cmd[1]] = cmd[2:]

    def DeleteGroup(self, cmd):
        if cmd[1] not in self.groups:
            print(f"{Color.RED}Group doesn't exist!{Color.ENDC}")
        else:
            self.groups.pop(cmd[1])
            print(Color.GREEN + cmd[1] + f" succesfully deleted!{Color.ENDC}")

    def ListGroups(self, cmd):
        for group in self.groups:
            print('{:<10}{:>19}'.format(group, self.groups[group]))

    def ImportRecords(self, file):
        try:
            f = open(file,"r",encoding="utf-8")
            for line in f:
                self.Action(line.split())
            f.close()
            return True
        except FileNotFoundError:
            print(f"{Color.RED}File not found!{Color.ENDC}")
            return False

    def Import(self, cmd):
        if self.ImportRecords(cmd[1]+".txt"):
            print(f"{Color.GREEN}Succesfully imported!{Color.ENDC}")

    def Export(self, cmd):
        try:
            f = open(cmd[1]+".txt","x",encoding="utf-8")
            for r in self.records.values():
                for i in r:
                    f.write(f"{i} ")
                f.write("\n")
            for g in self.groups:
                f.write(f"agr {g}")
            f.close()
            print(f"{Color.GREEN}Succesfully exported!{Color.ENDC}")
        except FileExistsError:
            print(f"{Color.RED}File exists!{Color.ENDC}")

    def Delete(self):
        self.fileName = ""
        self.openMode = False
        self.entities = dict()
        self.records = dict()
        self.id = 0

    def Open(self, cmd):
        self.Delete()
        self.fileName = cmd[1]+".txt"
        if self.ImportRecords(self.fileName):
            self.openMode = True
            print(f"{Color.GREEN}Succesfully opened{Color.ENDC}")

    def Close(self, cmd):
        self.Delete()

    def Reset(self, cmd):
        x = input("Are you sure? (y/n): ")
        if x == "y":
            self.Delete()
            print(f"{Color.GREEN}Succesfully reseted{Color.ENDC}")

    def Save(self, cmd):
        try:
            f = open(cmd[1]+".txt", "x", encoding="utf-8")
        except FileExistsError:
            print(f"{Color.RED}File exists!{Color.ENDC}")
            return 
        dash = lambda x : f.write(x * "-" + "\n")
        dash(26)
        f.write('{:<15}|{:>10}'.format("Name","Amount")+"\n")
        dash(26)
        for i in self.entities:
            f.write('{:<15}|{:>10}'.format(i,'{:.2f}'.format(round(self.entities[i][1],2)+0)) + "\n")
        f.write("\n")

        dash(47)
        f.write('{:<4}| {:<10}| {:<15}| {:<15}'.format("id","amount","payer", "debtor(s)")+"\n")
        dash(47)
        for r in self.records:
            rec = self.records[r]
            f.write('{:<4}| {:<10}| {:<15}| {}'.format(r, rec[2], rec[1], rec[3]))
            for i in range(4,len(rec)):
                f.write(f", {rec[i]}")
            f.write("\n")
        f.write(f"records: {len(self.records)}")
        print(f"{Color.GREEN}Succesfully saved{Color.ENDC}")

    def Help(self, cmd):
        for h in self.HELP:
            print(Color.SYS+'{:<10}'.format(h[0])+Color.ENDC+h[1])

    def Exit(self, cmd):
        self.run = False
        print(f"{Color.SYS}Good Bye!{Color.ENDC}")
    
    def Action(self, cmd):
        if cmd[0] not in self.KEYWORDS:
            print(f"{Color.RED}\"{cmd[0]}\" not a command{Color.ENDC}")
        else:
            self.KEYWORDS[cmd[0]](cmd)
    
    def Run(self):
        while self.run:
            self.Action(input("> ").split())

if __name__ == "__main__":
    os.system('color')
    p = a().Run()
    



