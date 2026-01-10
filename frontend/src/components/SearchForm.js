import React, { useState } from 'react';
import { Form, Button, Row, Col, InputGroup } from 'react-bootstrap';

function SearchForm({ onSearch, isLoading }) {
  const [formData, setFormData] = useState({
    sq_ft: '',
    total_hours: '',
    total_fee: '',
    total_spent: '',
    max_results: 5,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Build search params, only including non-empty values
    const params = {};

    if (formData.sq_ft) params.sq_ft = parseInt(formData.sq_ft, 10);
    if (formData.total_hours) params.total_hours = parseFloat(formData.total_hours);
    if (formData.total_fee) params.total_fee = parseFloat(formData.total_fee);
    if (formData.total_spent) params.total_spent = parseFloat(formData.total_spent);
    params.max_results = parseInt(formData.max_results, 10);

    onSearch(params);
  };

  const handleClear = () => {
    setFormData({
      sq_ft: '',
      total_hours: '',
      total_fee: '',
      total_spent: '',
      max_results: 5,
    });
  };

  return (
    <div className="search-form-container p-3">
      <h5 className="form-section-title">Search for recent proposals of similar size and scope</h5>

      <Form onSubmit={handleSubmit}>
        <Row className="mb-2">
          <Col md={6}>
            <Form.Group className="mb-2">
              <Form.Label>Square Feet</Form.Label>
              <Form.Control
                type="number"
                name="sq_ft"
                value={formData.sq_ft}
                onChange={handleChange}
                placeholder="Enter square footage"
                min="0"
              />
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group className="mb-2">
              <Form.Label>Total Hours</Form.Label>
              <Form.Control
                type="number"
                name="total_hours"
                value={formData.total_hours}
                onChange={handleChange}
                placeholder="Engineering + Drafting + Manager"
                min="0"
                step="0.5"
              />
            </Form.Group>
          </Col>
        </Row>

        <Row className="mb-2">
          <Col md={6}>
            <Form.Group className="mb-2">
              <Form.Label>Total Fee</Form.Label>
              <InputGroup>
                <InputGroup.Text>$</InputGroup.Text>
                <Form.Control
                  type="number"
                  name="total_fee"
                  value={formData.total_fee}
                  onChange={handleChange}
                  placeholder="SD + DD + CD"
                  min="0"
                  step="100"
                />
              </InputGroup>
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group className="mb-2">
              <Form.Label>Total Spent</Form.Label>
              <InputGroup>
                <InputGroup.Text>$</InputGroup.Text>
                <Form.Control
                  type="number"
                  name="total_spent"
                  value={formData.total_spent}
                  onChange={handleChange}
                  placeholder="SD + DD + CD"
                  min="0"
                  step="100"
                />
              </InputGroup>
            </Form.Group>
          </Col>
        </Row>

        <hr className="my-2" />

        <Row className="align-items-end">
          <Col md={4}>
            <Form.Group className="mb-2">
              <Form.Label>Maximum historical bids</Form.Label>
              <Form.Select
                name="max_results"
                value={formData.max_results}
                onChange={handleChange}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                  <option key={num} value={num}>
                    {num}
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
          </Col>
          <Col md={8} className="text-end">
            <Button
              variant="outline-secondary"
              onClick={handleClear}
              className="me-2 mb-3"
              disabled={isLoading}
            >
              Clear
            </Button>
            <Button
              variant="primary"
              type="submit"
              className="mb-3"
              disabled={isLoading}
            >
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
          </Col>
        </Row>
      </Form>
    </div>
  );
}

export default SearchForm;
