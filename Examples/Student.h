//
// Created by fgh on 18-7-2.
//

#ifndef FIRST_WEEK_STUDENT_H
#define FIRST_WEEK_STUDENT_H


#include "User.h"

class Student: public User {
protected:
    int iNumber;              /*学号*/
    float fChinese;           /*语文成绩*/
    float fMath;              /*数学成绩*/
    float fEnglish;           /*英语成绩*/
    float fAverage;           /*平均成绩*/
    int   iRank;              /*名次*/
    Student * pNext;          /*下级链表指针*/
public:
    Student();
    Student(std::string &acName, int iNumber, float chinese, float math, float english);
    Student(const Student& student);
    ~Student()override ;

    std::string get_name()const override ;
    void set_name(std::string acName)override ;
    virtual Student * get_pNext()const;
    virtual void set_pNext(Student* pnext);

    float get_fChinese()const ;
    float get_fEnglish()const ;
    float get_fMath()const ;
    float get_fAverage()const ;
    float update_fAverage() ;
    int get_iRank()const ;
    int get_iNumber()const ;

    void set_fChinese(float new_score);
    void set_fEnglish(float new_score);
    void set_fMath(float new_score);
    void set_iNumber(int new_num);
    void set_iRank(int new_rank);

    void show()const override ;
    void _show_rank()const ;
private:
    double cal_average()const ;
//不在对象层添加对数据合理性的检查，而在高级管理类读数据操作前进行检查
};


#endif //FIRST_WEEK_STUDENT_H
