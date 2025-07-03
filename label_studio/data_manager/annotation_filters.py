"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import json
from typing import Any, Dict, List, Optional

from django.db.models import Q, QuerySet
from tasks.models import Annotation


class AnnotationContentFilter:
    """
    Filter tasks based on annotation content (labels, choices, attributes)
    
    Supports filtering by:
    - Labels (rectanglelabels, polygonlabels, keypointlabels, etc.)
    - Choices (dropdown selections, radio buttons, etc.)
    - Text values (textarea content)
    - Numeric values (number inputs, ratings)
    - Existence of specific annotation types
    """
    
    @staticmethod
    def filter_by_label(queryset: QuerySet, label_name: str, operator: str = 'contains') -> QuerySet:
        """
        Filter tasks that have annotations with specific labels
        
        Args:
            queryset: Base queryset to filter
            label_name: The label to search for (e.g., 'car', 'person', 'license_plate')
            operator: 'contains', 'equal', 'not_contains'
        
        Returns:
            Filtered queryset
        """
        if operator == 'contains':
            # Find annotations where any result contains the label
            q = Q(
                annotations__result__contains=[{
                    'value': {
                        'rectanglelabels': [label_name]
                    }
                }]
            ) | Q(
                annotations__result__contains=[{
                    'value': {
                        'polygonlabels': [label_name]
                    }
                }]
            ) | Q(
                annotations__result__contains=[{
                    'value': {
                        'keypointlabels': [label_name]
                    }
                }]
            ) | Q(
                annotations__result__contains=[{
                    'value': {
                        'ellipselabels': [label_name]
                    }
                }]
            )
            
        elif operator == 'not_contains':
            # Exclude tasks that have the label
            q = ~Q(
                annotations__result__contains=[{
                    'value': {
                        'rectanglelabels': [label_name]
                    }
                }]
            ) & ~Q(
                annotations__result__contains=[{
                    'value': {
                        'polygonlabels': [label_name]
                    }
                }]
            ) & ~Q(
                annotations__result__contains=[{
                    'value': {
                        'keypointlabels': [label_name]
                    }
                }]
            )
            
        else:  # equal
            # Exact match for labels
            q = Q(
                annotations__result__exact=[{
                    'value': {
                        'rectanglelabels': [label_name]
                    }
                }]
            ) | Q(
                annotations__result__exact=[{
                    'value': {
                        'polygonlabels': [label_name]
                    }
                }]
            )
            
        return queryset.filter(q).distinct()
    
    @staticmethod
    def filter_by_choice(queryset: QuerySet, choice_value: str, from_name: str = None, operator: str = 'contains') -> QuerySet:
        """
        Filter tasks by choice selections (dropdown, radio, checkbox)
        
        Args:
            queryset: Base queryset to filter
            choice_value: The choice value to search for (e.g., 'nissan', 'white', 'sedan')
            from_name: Optional control name to narrow search
            operator: 'contains', 'equal', 'not_contains'
        
        Returns:
            Filtered queryset
        """
        if operator == 'contains':
            q = Q(
                annotations__result__contains=[{
                    'value': {
                        'choices': [choice_value]
                    }
                }]
            )
            if from_name:
                q &= Q(annotations__result__contains=[{'from_name': from_name}])
                
        elif operator == 'not_contains':
            q = ~Q(
                annotations__result__contains=[{
                    'value': {
                        'choices': [choice_value]
                    }
                }]
            )
            if from_name:
                q &= Q(annotations__result__contains=[{'from_name': from_name}])
                
        else:  # equal
            q = Q(
                annotations__result__exact=[{
                    'value': {
                        'choices': [choice_value]
                    }
                }]
            )
            if from_name:
                q &= Q(annotations__result__contains=[{'from_name': from_name}])
                
        return queryset.filter(q).distinct()
    
    @staticmethod
    def filter_by_text_content(queryset: QuerySet, text_content: str, from_name: str = None, operator: str = 'contains') -> QuerySet:
        """
        Filter tasks by text annotation content (textarea, text inputs)
        
        Args:
            queryset: Base queryset to filter
            text_content: Text to search for
            from_name: Optional control name
            operator: 'contains', 'equal', 'starts_with', 'ends_with'
        """
        if operator == 'contains':
            q = Q(annotations__result__icontains=text_content)
        elif operator == 'equal':
            q = Q(
                annotations__result__contains=[{
                    'value': {
                        'text': [text_content]
                    }
                }]
            )
        elif operator == 'starts_with':
            q = Q(annotations__result__iregex=rf'"text":\s*\[?\s*"{text_content}.*"')
        elif operator == 'ends_with':
            q = Q(annotations__result__iregex=rf'"text":\s*\[?\s*".*{text_content}"')
        else:
            q = Q(annotations__result__icontains=text_content)
            
        if from_name:
            q &= Q(annotations__result__contains=[{'from_name': from_name}])
            
        return queryset.filter(q).distinct()
    
    @staticmethod
    def filter_by_annotation_type(queryset: QuerySet, annotation_type: str, operator: str = 'exists') -> QuerySet:
        """
        Filter tasks by annotation type existence
        
        Args:
            queryset: Base queryset to filter
            annotation_type: Type to search for (rectanglelabels, polygonlabels, choices, etc.)
            operator: 'exists', 'not_exists'
        """
        if operator == 'exists':
            q = Q(annotations__result__contains=[{'type': annotation_type}])
        else:  # not_exists
            q = ~Q(annotations__result__contains=[{'type': annotation_type}])
            
        return queryset.filter(q).distinct()
    
    @staticmethod
    def filter_by_numeric_value(queryset: QuerySet, value: float, from_name: str = None, operator: str = 'equal') -> QuerySet:
        """
        Filter tasks by numeric annotation values (ratings, numbers)
        
        Args:
            queryset: Base queryset to filter
            value: Numeric value to filter by
            from_name: Optional control name
            operator: 'equal', 'greater', 'less', 'greater_or_equal', 'less_or_equal'
        """
        if operator == 'equal':
            q = Q(
                annotations__result__contains=[{
                    'value': {
                        'number': value
                    }
                }]
            ) | Q(
                annotations__result__contains=[{
                    'value': {
                        'rating': value
                    }
                }]
            )
        else:
            # For non-equality comparisons, we need to use JSONField queries
            # This is database-specific and might need adjustment for different DBs
            if operator == 'greater':
                q = Q(annotations__result__contains=[{'value': {'number__gt': value}}]) | \
                    Q(annotations__result__contains=[{'value': {'rating__gt': value}}])
            elif operator == 'less':
                q = Q(annotations__result__contains=[{'value': {'number__lt': value}}]) | \
                    Q(annotations__result__contains=[{'value': {'rating__lt': value}}])
            elif operator == 'greater_or_equal':
                q = Q(annotations__result__contains=[{'value': {'number__gte': value}}]) | \
                    Q(annotations__result__contains=[{'value': {'rating__gte': value}}])
            elif operator == 'less_or_equal':
                q = Q(annotations__result__contains=[{'value': {'number__lte': value}}]) | \
                    Q(annotations__result__contains=[{'value': {'rating__lte': value}}])
            else:
                q = Q(
                    annotations__result__contains=[{
                        'value': {
                            'number': value
                        }
                    }]
                )
                
        if from_name:
            q &= Q(annotations__result__contains=[{'from_name': from_name}])
            
        return queryset.filter(q).distinct()
    
    @staticmethod
    def filter_by_complex_query(queryset: QuerySet, filters: List[Dict[str, Any]]) -> QuerySet:
        """
        Filter tasks by complex annotation queries combining multiple criteria
        
        Args:
            queryset: Base queryset to filter
            filters: List of filter dictionaries with keys:
                - type: 'label', 'choice', 'text', 'number', 'exists'
                - value: Value to filter by
                - from_name: Optional control name
                - operator: Comparison operator
                - conjunction: 'and' or 'or' (for combining with next filter)
        
        Example filters:
        [
            {
                'type': 'label',
                'value': 'car',
                'operator': 'contains',
                'conjunction': 'and'
            },
            {
                'type': 'choice',
                'value': 'nissan',
                'from_name': 'car_brand',
                'operator': 'contains'
            }
        ]
        """
        if not filters:
            return queryset
            
        final_q = Q()
        current_q = None
        
        for i, filter_config in enumerate(filters):
            filter_type = filter_config.get('type')
            value = filter_config.get('value')
            from_name = filter_config.get('from_name')
            operator = filter_config.get('operator', 'contains')
            conjunction = filter_config.get('conjunction', 'and')
            
            if filter_type == 'label':
                q = AnnotationContentFilter._get_label_q(value, operator)
            elif filter_type == 'choice':
                q = AnnotationContentFilter._get_choice_q(value, from_name, operator)
            elif filter_type == 'text':
                q = AnnotationContentFilter._get_text_q(value, from_name, operator)
            elif filter_type == 'number':
                q = AnnotationContentFilter._get_numeric_q(value, from_name, operator)
            elif filter_type == 'exists':
                q = AnnotationContentFilter._get_exists_q(value, operator)
            else:
                continue
                
            if current_q is None:
                current_q = q
            else:
                if conjunction == 'and':
                    current_q &= q
                else:  # or
                    current_q |= q
                    
        if current_q:
            final_q = current_q
            
        return queryset.filter(final_q).distinct()
    
    @staticmethod
    def _get_label_q(label_name: str, operator: str) -> Q:
        """Helper method to build Q object for label filtering"""
        label_types = ['rectanglelabels', 'polygonlabels', 'keypointlabels', 'ellipselabels', 'brushlabels']
        
        if operator == 'contains':
            q = Q()
            for label_type in label_types:
                q |= Q(annotations__result__contains=[{'value': {label_type: [label_name]}}])
        elif operator == 'not_contains':
            q = Q()
            for label_type in label_types:
                q &= ~Q(annotations__result__contains=[{'value': {label_type: [label_name]}}])
        else:  # equal
            q = Q()
            for label_type in label_types:
                q |= Q(annotations__result__exact=[{'value': {label_type: [label_name]}}])
                
        return q
    
    @staticmethod
    def _get_choice_q(choice_value: str, from_name: str, operator: str) -> Q:
        """Helper method to build Q object for choice filtering"""
        if operator == 'contains':
            q = Q(annotations__result__contains=[{'value': {'choices': [choice_value]}}])
        elif operator == 'not_contains':
            q = ~Q(annotations__result__contains=[{'value': {'choices': [choice_value]}}])
        else:  # equal
            q = Q(annotations__result__exact=[{'value': {'choices': [choice_value]}}])
            
        if from_name:
            q &= Q(annotations__result__contains=[{'from_name': from_name}])
            
        return q
    
    @staticmethod
    def _get_text_q(text_content: str, from_name: str, operator: str) -> Q:
        """Helper method to build Q object for text filtering"""
        if operator == 'contains':
            q = Q(annotations__result__icontains=text_content)
        elif operator == 'equal':
            q = Q(annotations__result__contains=[{'value': {'text': [text_content]}}])
        else:
            q = Q(annotations__result__icontains=text_content)
            
        if from_name:
            q &= Q(annotations__result__contains=[{'from_name': from_name}])
            
        return q
    
    @staticmethod
    def _get_numeric_q(value: float, from_name: str, operator: str) -> Q:
        """Helper method to build Q object for numeric filtering"""
        q = Q(annotations__result__contains=[{'value': {'number': value}}]) | \
            Q(annotations__result__contains=[{'value': {'rating': value}}])
            
        if from_name:
            q &= Q(annotations__result__contains=[{'from_name': from_name}])
            
        return q
    
    @staticmethod
    def _get_exists_q(annotation_type: str, operator: str) -> Q:
        """Helper method to build Q object for existence filtering"""
        if operator == 'exists':
            return Q(annotations__result__contains=[{'type': annotation_type}])
        else:  # not_exists
            return ~Q(annotations__result__contains=[{'type': annotation_type}])


def get_annotation_labels_from_project(project):
    """
    Extract all unique labels used in annotations for a project
    
    Returns:
        Dict with label types as keys and lists of labels as values
    """
    annotations = Annotation.objects.filter(project=project, was_cancelled=False)
    labels = {
        'rectanglelabels': set(),
        'polygonlabels': set(),
        'keypointlabels': set(),
        'ellipselabels': set(),
        'brushlabels': set(),
        'choices': set(),
    }
    
    for annotation in annotations:
        if not annotation.result:
            continue
            
        try:
            if isinstance(annotation.result, str):
                result = json.loads(annotation.result)
            else:
                result = annotation.result
                
            for item in result:
                if 'value' in item:
                    value = item['value']
                    for label_type in labels.keys():
                        if label_type in value and isinstance(value[label_type], list):
                            labels[label_type].update(value[label_type])
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
            
    # Convert sets to sorted lists
    return {k: sorted(list(v)) for k, v in labels.items() if v}


def get_annotation_choices_from_project(project):
    """
    Extract all unique choice values used in annotations for a project
    
    Returns:
        Dict with from_name as keys and lists of choices as values
    """
    annotations = Annotation.objects.filter(project=project, was_cancelled=False)
    choices = {}
    
    for annotation in annotations:
        if not annotation.result:
            continue
            
        try:
            if isinstance(annotation.result, str):
                result = json.loads(annotation.result)
            else:
                result = annotation.result
                
            for item in result:
                if item.get('type') == 'choices' and 'from_name' in item and 'value' in item:
                    from_name = item['from_name']
                    if from_name not in choices:
                        choices[from_name] = set()
                    
                    if 'choices' in item['value']:
                        choices[from_name].update(item['value']['choices'])
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
            
    # Convert sets to sorted lists
    return {k: sorted(list(v)) for k, v in choices.items() if v}