import React, { useState } from 'react';
import { Form, Button, Row, Col, InputGroup } from 'react-bootstrap';

function SearchForm({ onSearch, isLoading }) {
  const [formData, setFormData] = useState({
    total_sheets: '',
    engineering_hrs: '',
    drafting_hrs: '',
    manager_hrs: '',
    cd_fee: '',
    ca_fee: '',
    sq_ft: '',
    total_spent_cd: '',
    total_spent_ca: '',
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

    if (formData.total_sheets) params.total_sheets = parseInt(formData.total_sheets, 10);
    if (formData.engineering_hrs) params.engineering_hrs = parseFloat(formData.engineering_hrs);
    if (formData.drafting_hrs) params.drafting_hrs = parseFloat(formData.drafting_hrs);
    if (formData.manager_hrs) params.manager_hrs = parseFloat(formData.manager_hrs);
    if (formData.cd_fee) params.cd_fee = parseFloat(formData.cd_fee);
    if (formData.ca_fee) params.ca_fee = parseFloat(formData.ca_fee);
    if (formData.sq_ft) params.sq_ft = parseInt(formData.sq_ft, 10);
    if (formData.total_spent_cd) params.total_spent_cd = parseFloat(formData.total_spent_cd);
    if (formData.total_spent_ca) params.total_spent_ca = parseFloat(formData.total_spent_ca);
    params.max_results = parseInt(formData.max_results, 10);

    onSearch(params);
  };

  const handleClear = () => {
    setFormData({
      total_sheets: '',
      engineering_hrs: '',
      drafting_hrs: '',
      manager_hrs: '',
      cd_fee: '',
      ca_fee: '',
      sq_ft: '',
      total_spent_cd: '',
      total_spent_ca: '',
      max_results: 5,
    });
  };

  return (
    <div className="search-form-container p-4">
      <h5 className="form-section-title">Search for recent proposals of similar size and scope</h5>

      <Form onSubmit={handleSubmit}>
        <Row className="mb-3">
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Total Sheets</Form.Label>
              <Form.Control
                type="number"
                name="total_sheets"
                value={formData.total_sheets}
                onChange={handleChange}
                placeholder="Enter total sheets"
                min="0"
              />
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>SQ FT</Form.Label>
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
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Total Engineering Hrs.</Form.Label>
              <Form.Control
                type="number"
                name="engineering_hrs"
                value={formData.engineering_hrs}
                onChange={handleChange}
                placeholder="Enter hours"
                min="0"
                step="0.5"
              />
            </Form.Group>
          </Col>
        </Row>

        <Row className="mb-3">
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Total Drafting Hrs.</Form.Label>
              <Form.Control
                type="number"
                name="drafting_hrs"
                value={formData.drafting_hrs}
                onChange={handleChange}
                placeholder="Enter hours"
                min="0"
                step="0.5"
              />
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Total Manager/Reviewer Hrs.</Form.Label>
              <Form.Control
                type="number"
                name="manager_hrs"
                value={formData.manager_hrs}
                onChange={handleChange}
                placeholder="Enter hours"
                min="0"
                step="0.5"
              />
            </Form.Group>
          </Col>
          <Col md={4}>
            {/* Empty column for alignment */}
          </Col>
        </Row>

        <Row className="mb-3">
          <Col md={6}>
            <Form.Group className="mb-3">
              <Form.Label>CD Fee</Form.Label>
              <InputGroup>
                <InputGroup.Text>$</InputGroup.Text>
                <Form.Control
                  type="number"
                  name="cd_fee"
                  value={formData.cd_fee}
                  onChange={handleChange}
                  placeholder="Enter CD fee"
                  min="0"
                  step="100"
                />
              </InputGroup>
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group className="mb-3">
              <Form.Label>CA Fee</Form.Label>
              <InputGroup>
                <InputGroup.Text>$</InputGroup.Text>
                <Form.Control
                  type="number"
                  name="ca_fee"
                  value={formData.ca_fee}
                  onChange={handleChange}
                  placeholder="Enter CA fee"
                  min="0"
                  step="100"
                />
              </InputGroup>
            </Form.Group>
          </Col>
        </Row>

        <Row className="mb-3">
          <Col md={6}>
            <Form.Group className="mb-3">
              <Form.Label>Total $ spent CD</Form.Label>
              <InputGroup>
                <InputGroup.Text>$</InputGroup.Text>
                <Form.Control
                  type="number"
                  name="total_spent_cd"
                  value={formData.total_spent_cd}
                  onChange={handleChange}
                  placeholder="Enter total spent on CD"
                  min="0"
                  step="100"
                />
              </InputGroup>
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group className="mb-3">
              <Form.Label>Total $ spent CA</Form.Label>
              <InputGroup>
                <InputGroup.Text>$</InputGroup.Text>
                <Form.Control
                  type="number"
                  name="total_spent_ca"
                  value={formData.total_spent_ca}
                  onChange={handleChange}
                  placeholder="Enter total spent on CA"
                  min="0"
                  step="100"
                />
              </InputGroup>
            </Form.Group>
          </Col>
        </Row>

        <hr className="my-4" />

        <Row className="align-items-end">
          <Col md={4}>
            <Form.Group className="mb-3">
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
