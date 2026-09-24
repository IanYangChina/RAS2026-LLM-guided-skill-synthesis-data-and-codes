## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4920 | 0.87 | ❌ rejected |
| 5 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | 0.6604 | 0.96 | ❌ rejected |
| 4 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | 0.6534 | 0.95 | ❌ rejected |
| 3 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | time_limit | time_limit | 7 | 0.5033 | 0.85 | ❌ rejected |
| 2 | approach → descend | arc_cartesian | linear_cartesian | position_control | position_control | pose_tolerance | pose_tolerance | 6 | 0.6606 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: obstacle_reach
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.5
- Force limit: 5.0 N
- Obstacle body: obstacle_block (contact = collision penalty)
- Primary evaluation target: **TCP distance to goal position (Gaussian proximity kernel)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.492) — your mutation base

```yaml
skill: obstacle_reach
dsl_version: 2
subtasks:
- id: approach_over_obstacle
  offset:
  - 0.0
  - 0.0
  - 0.25
  weight: 0.3
- id: reach_goal
  weight: 0.7
phases:
- id: approach_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.25
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_over_obstacle
- id: descend_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.25], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.492
- **task_score** (E): 0.872
- **fitness_score**: 0.872  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| clear_obstacle | 0.33 | 0.00 | 0.3615 |
| move_above_goal | 0.67 | 0.00 | 0.1314 |
| descend_goal | 1.00 | 0.00 | 0.2561 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| clear_obstacle | approach | 0.33 / step_budget | (0.350, -0.000, 0.321)→(0.635, 0.003, 0.541) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.742→0.742 | 0.00 / 0.000 | 0.000 | 0.000 |
| move_above_goal | approach | 0.67 / step_budget | (0.635, 0.003, 0.541)→(0.692, 0.005, 0.423) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.742→0.742 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_goal | descend | 1.00 / step_budget | (0.692, 0.005, 0.423)→(0.721, 0.005, 0.170) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.742→0.742 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- obstacle_clearance: 0.870
- path_efficiency: 0.498
- arc_smoothness: 0.991
- collision_factor: 1.000  (exp(−peak_force / force_scale))
- peak_obstacle_force: 0.000 N
- collision_location: obstacle_block  (or None if no contact)
- final_tcp_distance: 0.019
- min_tcp_distance: 0.019
- tcp_proximity_score: 0.879
- goal_reached_rate: 1.000
- peak_obstacle_counterbody: None
- peak_obstacle_countergeom: None
- peak_obstacle_obstacle_body: None
- peak_obstacle_obstacle_geom: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.879
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.879
- **Median Q (composite search score)**: 0.499
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.448


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d910c77cb638a69341ed671296c717a208cd48823489ef9211f18ea0e1b939e7`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `f90839fb981b04e986bac696c468b50f4838fff85cbd7f5c1f7b2ee178b7b0de`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":36.0,"average_failure_rate":0.15385,"average_mean_iterations":33.87179,"average_solve_count":234.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"clear_obstacle.phase1_arc_height":0.06177,"clear_obstacle.phase1_speed":0.11336,"clear_obstacle.phase1_z_offset":0.40529,"descend_goal.descend_speed":0.06361,"descend_goal.descend_tolerance":0.0293,"move_above_goal.phase2_speed":0.09054,"move_above_goal.phase2_z_offset":0.29748},"optimized_scores":{"best_composite_score":0.4788,"best_fitness_score":0.8588,"best_task_score":0.8588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02283,"key_states":{"actual_goal_position":[0.74431,0.00113,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.737,0.001,0.17163],"realised_goal_position":[0.74431,0.00113,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"clear_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"clear_obstacle","tcp_end":[0.63902,0.00078,0.53547],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.83371,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":55.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"above_goal","tcp_end":[0.66084,0.00079,0.5161],"tcp_start":[0.63902,0.00078,0.53547],"tcp_to_object_dist_end":0.83849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.75927,"object_to_goal_dist_start":0.75927,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.737,0.001,0.17163],"tcp_start":[0.66084,0.00079,0.5161],"tcp_to_object_dist_end":0.75672,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `94e78c883a04c29d3c37cc716fa077d5c59698d148b7b4f0e399907a3c99cbc8`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.11236,"average_mean_iterations":25.97753,"average_solve_count":178.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"clear_obstacle.phase1_arc_height":0.07914,"clear_obstacle.phase1_speed":0.10012,"clear_obstacle.phase1_z_offset":0.45462,"descend_goal.descend_speed":0.13053,"descend_goal.descend_tolerance":0.01848,"move_above_goal.phase2_speed":0.11481,"move_above_goal.phase2_z_offset":0.18254},"optimized_scores":{"best_composite_score":0.49867,"best_fitness_score":0.87867,"best_task_score":0.87867},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.0194,"key_states":{"actual_goal_position":[0.7305,0.03079,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.72672,0.03042,0.16903],"realised_goal_position":[0.7305,0.03079,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"clear_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"clear_obstacle","tcp_end":[0.60869,0.02067,0.57957],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.84073,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"above_goal","tcp_end":[0.71975,0.02972,0.34879],"tcp_start":[0.60869,0.02067,0.57957],"tcp_to_object_dist_end":0.80036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":278.0,"n_steps_budget":960.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.74638,"object_to_goal_dist_start":0.74638,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.72672,0.03042,0.16903],"tcp_start":[0.71975,0.02972,0.34879],"tcp_to_object_dist_end":0.74674,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `4545dd6ce27d481eea1784f20773d493eb22fff73af3521a1f048df5cf49bcf3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.03529,"average_mean_iterations":10.8,"average_solve_count":170.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"clear_obstacle.phase1_arc_height":0.06825,"clear_obstacle.phase1_speed":0.08746,"clear_obstacle.phase1_z_offset":0.35655,"descend_goal.descend_speed":0.13727,"descend_goal.descend_tolerance":0.01367,"move_above_goal.phase2_speed":0.07025,"move_above_goal.phase2_z_offset":0.23762},"optimized_scores":{"best_composite_score":0.4986,"best_fitness_score":0.8786,"best_task_score":0.8786},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01941,"key_states":{"actual_goal_position":[0.70382,-0.01567,0.15],"actual_obstacle_position":[0.5,0.0,0.15],"final_tcp_position":[0.70029,-0.01572,0.16909],"realised_goal_position":[0.70382,-0.01567,0.15],"realised_object_initial_position":[0.0,0.0,0.0],"realised_obstacle_position":[0.5,0.0,0.15]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":968.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"clear_obstacle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"clear_obstacle","tcp_end":[0.65674,-0.01349,0.50654],"tcp_start":[0.3503,-0.0,0.32087],"tcp_to_object_dist_end":0.8295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"move_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"above_goal","tcp_end":[0.6944,-0.01532,0.40463],"tcp_start":[0.65674,-0.01349,0.50654],"tcp_to_object_dist_end":0.80383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.71979,"object_to_goal_dist_start":0.71979,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.70029,-0.01572,0.16909],"tcp_start":[0.6944,-0.01532,0.40463],"tcp_to_object_dist_end":0.72059,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```