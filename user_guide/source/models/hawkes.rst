================
3.1 Hawkes Model
================

Hawkes model is an implementation of Bivariate Hawkes process for modelling 
high frequency financial transaction data::

    >>> from va.models.hawkes import hawkes
    >>> myHawkes = hawkes()
    >>> myHawkes.fit(Price)
    >>> myHawkes.predict(ahead = 2)



